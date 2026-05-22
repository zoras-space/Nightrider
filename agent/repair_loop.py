"""The Night Drive Loop: build, test, inspect, repair, repeat."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from agent import file_editor, logger
from agent.command_runner import CommandResult, run_command
from agent.config import AgentConfig
from agent.model_client import OllamaClient
from agent.prompts import FAILURE_ANALYSIS_PROMPT, INITIAL_CODE_PROMPT, PATCH_PROMPT
from agent.report_writer import write_final_report
from agent.sanity import apply_python_sanity_repairs
from agent import terminal_ui


FAILURE_HINTS = {
    "missing nonempty_line_count": """
The output JSON schema is incomplete.

Required field missing:
- nonempty_line_count

The program must:
- count lines whose stripped content is not empty
- add the value to the final JSON output

Suggested implementation:

nonempty_line_count = sum(
    1 for line in lines if line.strip()
)

Then include:

"nonempty_line_count": nonempty_line_count

inside the result dictionary before json.dumps().
""",
    "jsondecodeerror": """
The output is not valid JSON.

The program must:
- print ONLY valid JSON to stdout
- avoid debug prints
- avoid explanatory text
- ensure json.dumps() output is printed cleanly
""",
    "returncode": """
The program is returning the wrong exit code.

The program must:
- return nonzero exit code on failure
- return zero on success
- print human-readable errors to stderr
""",
}


@dataclass
class RepairState:
    failures: list[str] = field(default_factory=list)
    last_signature: str | None = None
    repeat_count: int = 0
    passed: bool = False
    rounds_completed: int = 0
    last_result: CommandResult | None = None
    failure_categories: list[str] = field(default_factory=list)
    visible_scores: list[str] = field(default_factory=list)
    repair_notes: list[str] = field(default_factory=list)


def enrich_failure_summary(summary: str) -> str:
    lowered = summary.lower()

    for key, hint in FAILURE_HINTS.items():
        if key in lowered:
            return summary + "\n\nRepair hint:\n" + hint

    return summary


def _failure_signature(result: CommandResult) -> str:
    combined = (result.stderr or result.stdout).strip()
    lines = [line.strip() for line in combined.splitlines() if line.strip()]
    signature = "\n".join(lines[-12:])
    signature = re.sub(r"/private/var/folders/[^ ]+", "<tmp-path>", signature)
    signature = re.sub(r"/tmp/[^ ]+", "<tmp-path>", signature)
    signature = re.sub(r"pytest-\d+", "pytest-<n>", signature)
    signature = re.sub(r"test_[A-Za-z0-9_]+0", "test_<case>", signature)
    signature = re.sub(r"line \d+", "line <n>", signature)
    return signature


def _shorten(text: str, limit: int = 6000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def _classify_failure(result: CommandResult) -> str:
    combined = f"{result.stdout}\n{result.stderr}".lower()

    if result.timed_out or "timeout" in combined or "timed out" in combined:
        return "runtime behavior"

    if (
        "nonempty_line_count" in combined
        or "keyerror" in combined
        or "right contains" in combined
    ):
        return "output format"

    if (
        "jsondecodeerror" in combined
        or "not valid json" in combined
        or "json.decoder" in combined
    ):
        return "output format"

    if (
        "assert result.returncode" in combined
        or "exit code" in combined
        or "returncode" in combined
    ):
        return "exit code"

    if (
        "filenotfounderror" in combined
        or "indexerror" in combined
        or "usage" in combined
        or "argument" in combined
    ):
        return "parsing"

    if "assert" in combined or "expected" in combined or "missing" in combined:
        return "missing functionality"

    return "unknown"


def _extract_visible_scores(result: CommandResult) -> list[str]:
    combined = f"{result.stdout}\n{result.stderr}"

    patterns = (
        r"score[^0-9]{0,12}([0-9]+(?:\.[0-9]+)?\s*/\s*[0-9]+(?:\.[0-9]+)?)",
        r"([0-9]+(?:\.[0-9]+)?\s*/\s*[0-9]+(?:\.[0-9]+)?)",
        r"([0-9]+(?:\.[0-9]+)?%)",
    )

    scores: list[str] = []

    for pattern in patterns:
        for match in re.findall(pattern, combined, flags=re.IGNORECASE):
            if match not in scores:
                scores.append(match)

    return scores[:5]


def _repair_action_for(category: str, failure_summary: str) -> str:
    if "nonempty_line_count" in failure_summary:
        return (
            "Add nonempty_line_count to the JSON output "
            "and compute it correctly."
        )

    if category == "output format":
        return "Fix the output JSON format, then rerun the tests."

    if category == "exit code":
        return "Fix the program exit behavior, then rerun the tests."

    if category == "parsing":
        return "Fix CLI argument parsing, then rerun the tests."

    if category == "runtime behavior":
        return "Fix the runtime error, then rerun the tests."

    if category == "missing functionality":
        return "Add the missing required behavior, then rerun the tests."

    return "Apply a targeted repair, then rerun the tests."


def generate_initial_code(
    client: OllamaClient,
    spec: str,
    plan: str,
    program_path: Path,
) -> None:
    prompt = INITIAL_CODE_PROMPT.format(
        spec=spec,
        plan=plan,
        program_path=program_path,
    )

    logger.log_prompt(prompt)

    response = client.generate(prompt)

    backup, change_summary = (
        file_editor.replace_file_from_model_with_summary(
            program_path,
            response.text,
            round_number=0,
        )
    )

    logger.log_decision(
        f"Initial solution generated at {program_path} using {response.model}.\n"
        f"Backup: {backup or '<none>'}\n"
        f"Change summary:\n{change_summary}"
    )


def analyze_failure(
    client: OllamaClient,
    summary: str,
    program_path: Path,
    command: str,
    result: CommandResult,
    failure_memory: list[str],
    score_memory: list[str],
) -> str:
    code = file_editor.inspect_file(program_path)

    prompt = FAILURE_ANALYSIS_PROMPT.format(
        summary=summary,
        code=_shorten(code),
        command=command,
        exit_code=result.exit_code,
        stdout=_shorten(result.stdout),
        stderr=_shorten(result.stderr),
        failure_memory="\n---\n".join(failure_memory[-3:]) or "<none>",
        score_memory="\n".join(score_memory[-5:]) or "<none>",
    )

    logger.log_prompt(prompt)

    response = client.generate(prompt)

    enriched = enrich_failure_summary(response.text)

    logger.log_decision(f"Failure analysis:\n{enriched}")

    return enriched


def request_patch(
    client: OllamaClient,
    summary: str,
    program_path: Path,
    failure_analysis: str,
    result: CommandResult,
    round_number: int,
) -> None:
    code = file_editor.inspect_file(program_path)

    prompt = PATCH_PROMPT.format(
        program_path=program_path,
        summary=summary,
        code=_shorten(code),
        failure_analysis=failure_analysis,
        stdout=_shorten(result.stdout),
        stderr=_shorten(result.stderr),
    )

    logger.log_prompt(prompt)

    response = client.generate(prompt)

    try:
        backup, change_summary = (
            file_editor.replace_file_from_model_with_summary(
                program_path,
                response.text,
                round_number=round_number,
            )
        )

    except ValueError as exc:
        logger.log_error(
            f"Rejected invalid model patch in round {round_number}: {exc}"
        )

        logger.log_decision(
            f"Rejected invalid model patch in round {round_number}; "
            "keeping previous program file."
        )

        return

    logger.log_decision(
        f"Applied round {round_number} targeted full-file patch. "
        f"Backup: {backup or '<none>'}\n"
        f"Change summary:\n{change_summary}"
    )


def run_repair_loop(
    config: AgentConfig,
    client: OllamaClient,
    spec: str,
    summary: str,
    plan: str,
) -> RepairState:
    logger.ensure_log_files(config.log_dir)

    state = RepairState()

    terminal_ui.print_action(
        "Generate initial solution",
        quiet=config.quiet,
    )

    generate_initial_code(
        client,
        spec,
        plan,
        config.program_path,
    )

    terminal_ui.print_changed_files(
        [str(config.program_path)],
        quiet=config.quiet,
    )

    for round_number in range(1, config.max_rounds + 1):
        terminal_ui.print_round_start(
            round_number,
            config.max_rounds,
            "Run tests",
            quiet=config.quiet,
        )

        terminal_ui.print_command(
            config.test_command,
            quiet=config.quiet,
        )

        result = run_command(
            config.test_command,
            timeout_seconds=config.timeout_seconds,
        )

        state.rounds_completed = round_number
        state.last_result = result

        logger.log_command(
            result.command,
            result.exit_code,
            result.stdout,
            result.stderr,
            result.duration,
        )

        logger.log_test_run(
            round_number,
            result.exit_code,
            result.stdout,
            result.stderr,
        )

        terminal_ui.print_test_result(
            result,
            quiet=config.quiet,
            verbose=config.verbose,
        )

        scores = _extract_visible_scores(result)

        if scores:
            state.visible_scores.extend(scores)

            logger.log_decision(
                f"Visible score signals in round {round_number}: "
                f"{', '.join(scores)}"
            )

        if result.exit_code == 0:
            state.passed = True

            logger.log_decision(
                f"Tests passed on round {round_number}. "
                "Night Drive Loop complete."
            )

            break

        failure_summary = terminal_ui.summarize_failure_text(
            result.stdout,
            result.stderr,
        )

        failure_summary = enrich_failure_summary(failure_summary)

        terminal_ui.print_failure_summary(
            failure_summary,
            quiet=config.quiet,
        )

        signature = _failure_signature(result)

        if signature == state.last_signature:
            state.repeat_count += 1
        else:
            state.repeat_count = 1
            state.last_signature = signature

        state.failures.append(signature)

        category = _classify_failure(result)

        state.failure_categories.append(category)

        logger.log_decision(
            f"Round {round_number} failure category: {category}"
        )

        if state.repeat_count >= 3:
            reason = (
                "Same failure signature repeated 3 times; "
                "stopping early to avoid unproductive looping."
            )

            logger.log_error(reason)
            logger.log_decision(reason)

            break

        if apply_python_sanity_repairs(
            config.program_path,
            round_number,
        ):
            note = (
                f"Applied deterministic sanity repair "
                f"for {category} failure."
            )

            state.repair_notes.append(note)

            terminal_ui.print_next_action(
                note,
                quiet=config.quiet,
            )

            terminal_ui.print_changed_files(
                [str(config.program_path)],
                quiet=config.quiet,
            )

            continue

        terminal_ui.print_next_action(
            _repair_action_for(category, failure_summary),
            quiet=config.quiet,
        )

        failure_analysis = analyze_failure(
            client,
            summary,
            config.program_path,
            config.test_command,
            result,
            state.failures,
            state.visible_scores,
        )

        terminal_ui.print_model_summary(
            "FAILURE ANALYSIS",
            failure_analysis,
            quiet=config.quiet,
            verbose=config.verbose,
        )

        request_patch(
            client,
            summary,
            config.program_path,
            failure_analysis,
            result,
            round_number,
        )

        state.repair_notes.append(
            f"Applied targeted model repair for {category} failure."
        )

        terminal_ui.print_changed_files(
            [str(config.program_path)],
            quiet=config.quiet,
        )

    run_context = _build_run_context(
        config,
        state,
        summary,
        plan,
    )

    write_final_report(
        client,
        run_context,
        log_dir=config.log_dir,
    )

    terminal_ui.print_final_report(
        config,
        state.passed,
        state.rounds_completed,
        state.repair_notes,
    )

    return state


def _build_run_context(
    config: AgentConfig,
    state: RepairState,
    summary: str,
    plan: str,
) -> str:
    last = state.last_result

    status = "passed" if state.passed else "not passed"

    return (
        f"Team: Nightrider\n"
        f"Model: {config.model}\n"
        f"Spec: {config.spec_path}\n"
        f"Program: {config.program_path}\n"
        f"Test command: {config.test_command}\n"
        f"Max rounds: {config.max_rounds}\n"
        f"Rounds completed: {state.rounds_completed}\n"
        f"Final status: {status}\n"
        f"Last exit code: {last.exit_code if last else '<none>'}\n\n"
        f"Spec summary:\n{summary}\n\n"
        f"Implementation plan:\n{plan}\n\n"
        f"Recent failures:\n"
        f"{chr(10).join(state.failures[-3:]) or '<none>'}\n"
        f"Failure categories:\n"
        f"{chr(10).join(state.failure_categories[-5:]) or '<none>'}\n"
        f"Visible score progression:\n"
        f"{chr(10).join(state.visible_scores[-10:]) or '<none>'}\n"
        f"Tools available: local Ollama model client, "
        f"safe file replacement with backups, subprocess "
        f"command runner, pytest-compatible test command, "
        f"timestamped logs.\n"
    )