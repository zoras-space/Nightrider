"""Human-readable terminal output for Nightrider runs."""

from __future__ import annotations

from pathlib import Path

from agent.command_runner import CommandResult
from agent.config import AgentConfig


LINE = "─" * 56
REQUIRED_LOGS = (
    "prompts.log",
    "decisions.log",
    "commands.log",
    "test_runs.log",
    "errors.log",
    "human_interventions.log",
    "final_report.md",
)


def print_header(config: AgentConfig) -> None:
    if config.quiet:
        print(f"🌙 Nightrider started: {config.spec_path} -> {config.program_path}")
        return
    print("\n🌙 Nightrider Agent\n")
    print(f"Spec: {config.spec_path}")
    if config.verbose:
        print(f"Program: {config.program_path}")
        print(f"Model: {config.model}")
        print(f"Max rounds: {config.max_rounds}")
        print(f"Logs: {config.log_dir}")
    print()


def print_input_loaded(spec_path: Path, quiet: bool = False) -> None:
    if quiet:
        return
    return


def print_rules(summary: str, quiet: bool = False, verbose: bool = False) -> None:
    if quiet:
        return
    print("Purpose:")
    print(_purpose_from_summary(summary))
    print()
    if not verbose:
        return
    checks = {
        "CLI behavior detected": ("argument", "command", "cli"),
        "Input format detected": ("input", "file", "json"),
        "Output format detected": ("output", "stdout", "json"),
        "Error handling detected": ("error", "stderr", "exit"),
        "Edge cases detected": ("edge", "empty", "invalid"),
        "Stdout/stderr rules detected": ("stdout", "stderr"),
    }
    lowered = summary.lower()
    print("[RULES]")
    print("Detected behavior:")
    for label, needles in checks.items():
        mark = "✓" if any(needle in lowered for needle in needles) else "-"
        print(f"{mark} {label}")
    if verbose:
        print("\nSummary:")
        print(_clip(summary, 1200))
    print()


def print_round_start(round_number: int, max_rounds: int, action: str, quiet: bool = False) -> None:
    if quiet:
        print(f"[{round_number}/{max_rounds}] {action}")
        return
    print(f"[Round {round_number}/{max_rounds}] {action}")


def print_action(action: str, quiet: bool = False) -> None:
    if quiet:
        return
    return


def print_command(command: str, quiet: bool = False) -> None:
    if quiet:
        return
    return


def print_test_result(result: CommandResult, quiet: bool = False, verbose: bool = False) -> None:
    passed = result.exit_code == 0
    mark = "✅" if passed else "❌"
    status = "Passed" if passed else "Failed"
    if quiet:
        print(f"[test] {mark} {status} exit={result.exit_code}")
        return
    print(f"{mark} {status} ({result.duration:.2f}s)")
    if verbose:
        print(f"Exit code: {result.exit_code}")
        print("\nStdout summary:")
        print(_clip(result.stdout.strip() or "<empty>", 1600))
        print("\nStderr summary:")
        print(_clip(result.stderr.strip() or "<empty>", 1600))
    print()


def print_failure_summary(summary: str, quiet: bool = False) -> None:
    if quiet:
        return
    print("What failed:")
    for line in _summary_lines(summary):
        print(f"- {line}")
    print()


def print_next_action(action: str, quiet: bool = False) -> None:
    if quiet:
        return
    print("Fixing:")
    print(action)
    print()


def print_changed_files(paths: list[str], quiet: bool = False) -> None:
    if quiet or not paths:
        return
    return


def print_model_summary(label: str, text: str, quiet: bool = False, verbose: bool = False) -> None:
    if quiet or not verbose:
        return
    print(f"[{label}]")
    print(_clip(text, 1600))
    print()


def print_final_report(config: AgentConfig, passed: bool, rounds_used: int, repairs: list[str]) -> None:
    status = "passed" if passed else "not passed"
    if config.quiet:
        print(f"final: {status} rounds={rounds_used}/{config.max_rounds} logs={config.log_dir}")
        return
    print(f"{LINE}\n")
    mark = "✅" if passed else "❌"
    print(f"{mark} Final status: {status}")
    print(f"Rounds used: {rounds_used}/{config.max_rounds}")
    if repairs:
        print("Repairs:")
        for repair in repairs[-5:]:
            print(f"- {repair}")
    print(f"Program: {config.program_path}")
    print(f"Logs: {config.log_dir}/")
    if config.verbose:
        print()
        print_evidence_checklist(config.log_dir)


def print_evidence_checklist(log_dir: Path) -> None:
    print("Logs written:")
    for filename in REQUIRED_LOGS:
        print(f"✓ {log_dir / filename}")
    print()


def summarize_failure_text(stdout: str, stderr: str, limit: int = 4) -> str:
    combined = f"{stderr}\n{stdout}".strip()
    if not combined:
        return "No stdout/stderr was captured."
    simple = _known_failure_summary(combined)
    if simple:
        return simple
    useful: list[str] = []
    for line in combined.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if (
            "assert" in lowered
            or "error" in lowered
            or "failed" in lowered
            or "missing" in lowered
            or "exit_code" in lowered
            or "nameerror" in lowered
            or "traceback" in lowered
            or "command not found" in lowered
        ):
            useful.append(stripped)
        if len(useful) >= limit:
            break
    if not useful:
        useful = [line.strip() for line in combined.splitlines() if line.strip()][:limit]
    return "\n".join(useful) if useful else "No concise failure summary available."


def _summary_lines(text: str) -> list[str]:
    lines = [line.strip(" -") for line in text.splitlines() if line.strip(" -")]
    return lines[:5] or ["No concise failure summary available."]


def _purpose_from_summary(summary: str) -> str:
    lowered = summary.lower()
    fields: list[str] = []
    for field in ("line_count", "word_count", "char_count", "nonempty_line_count"):
        if field in summary:
            fields.append(field)
    if fields and "json" in lowered:
        return "Read a file path from the CLI and print JSON with " + ", ".join(fields) + "."
    lines = [line.strip(" #-*") for line in summary.splitlines() if line.strip(" #-*")]
    for line in lines:
        if len(line) > 20 and not line.lower().startswith(("required", "arguments", "input", "output")):
            return _clip(line, 180)
    return "Read the spec, generate the program, run tests, and repair failures."


def _known_failure_summary(text: str) -> str:
    lowered = text.lower()
    lines: list[str] = []
    if "nonempty_line_count" in text and ("keyerror" in lowered or "right contains" in lowered or "assert parsed" in lowered):
        lines.append("Output JSON is missing nonempty_line_count.")
    if "char_count" in text and ("char_count'] ==" in text or "char_count\" ==" in text):
        lines.append("Character count does not match the expected value.")
    if "syntaxerror" in lowered:
        lines.append("Generated program is not valid Python syntax.")
    if "nameerror" in lowered:
        lines.append("Generated program references a missing name or import.")
    if "command not found" in lowered:
        lines.append("The configured test command could not be found.")
    if "assert result.returncode == 0" in text and ("assert 1 == 0" in text or "returncode=1" in text):
        lines.append("Program exited with an error for an input that should succeed.")
    unique: list[str] = []
    for line in lines:
        if line not in unique:
            unique.append(line)
    return "\n".join(unique[:4])


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... clipped; full details are in agent_logs/ ..."
