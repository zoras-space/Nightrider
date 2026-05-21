"""CLI entry point for the Nightrider autonomous coding-agent workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import logger  # noqa: E402
from agent.config import AgentConfig, resolve_model  # noqa: E402
from agent.model_client import OllamaClient  # noqa: E402
from agent.planner import create_plan, read_spec, summarize_spec  # noqa: E402
from agent.repair_loop import run_repair_loop  # noqa: E402
from agent import terminal_ui  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nightrider autonomous CLI challenge agent.")
    parser.add_argument("--spec", help="Path to the Markdown specification.")
    parser.add_argument("--program", default="workspace/solution.py", help="Target solution file to create or patch.")
    parser.add_argument("--test-command", help="Command used to run public or toy tests.")
    parser.add_argument("--max-rounds", type=int, default=8, help="Maximum build-test-repair rounds.")
    parser.add_argument("--model", help="Ollama model name. Overrides AGENT_MODEL.")
    parser.add_argument("--ollama-url", default="http://localhost:11434/api/generate", help="Ollama generate endpoint.")
    parser.add_argument("--timeout", type=int, default=60, help="Test command timeout in seconds.")
    parser.add_argument("--check-ollama", action="store_true", help="Check local Ollama availability, then exit.")
    parser.add_argument("--init-logs", action="store_true", help="Create required agent log files, then exit.")
    parser.add_argument("--verbose", action="store_true", help="Show command/model summaries in terminal output.")
    parser.add_argument("--quiet", action="store_true", help="Show only essential progress and final status.")
    parser.add_argument(
        "--log-human-intervention",
        help="Append a timestamped human intervention note, then exit.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    logger.ensure_log_files()

    if args.init_logs:
        logger.log_decision("Initialized required Nightrider log files.")
        print("[Nightrider] Agent logs initialized.")
        return 0

    if args.log_human_intervention:
        logger.log_human_intervention(args.log_human_intervention)
        print("[Nightrider] Human intervention logged.")
        return 0

    if args.check_ollama:
        model = resolve_model(args.model)
        client = OllamaClient(model=model, endpoint=args.ollama_url)
        ok, message = client.check_available()
        print(f"[Nightrider] {message}")
        return 0 if ok else 1

    missing = [name for name in ("spec", "test_command") if getattr(args, name) is None]
    if missing:
        parser.error(f"missing required arguments: {', '.join('--' + item.replace('_', '-') for item in missing)}")

    model = resolve_model(args.model)
    config = AgentConfig(
        spec_path=Path(args.spec),
        program_path=Path(args.program),
        test_command=args.test_command,
        max_rounds=args.max_rounds,
        model=model,
        ollama_url=args.ollama_url,
        timeout_seconds=args.timeout,
        verbose=args.verbose,
        quiet=args.quiet,
    )

    try:
        spec = read_spec(config.spec_path)
    except OSError as exc:
        logger.log_error(f"Could not read spec {config.spec_path}: {exc}")
        print(f"[Nightrider] Could not read spec: {exc}", file=sys.stderr)
        return 2

    terminal_ui.print_header(config)
    terminal_ui.print_input_loaded(config.spec_path, quiet=config.quiet)
    client = OllamaClient(model=model, endpoint=config.ollama_url)

    try:
        summary = summarize_spec(client, spec)
        terminal_ui.print_rules(summary, quiet=config.quiet, verbose=config.verbose)
        terminal_ui.print_model_summary("SPEC SUMMARY", summary, quiet=config.quiet, verbose=config.verbose)
        plan = create_plan(client, summary)
        terminal_ui.print_model_summary("IMPLEMENTATION PLAN", plan, quiet=config.quiet, verbose=config.verbose)
        state = run_repair_loop(config, client, spec, summary, plan)
    except Exception as exc:  # noqa: BLE001
        logger.log_error(f"Agent run failed: {exc}")
        print(f"[Nightrider] Agent run failed: {exc}", file=sys.stderr)
        return 1

    if state.passed:
        if config.verbose and not config.quiet:
            print("[Nightrider] Tests passed. Final report updated.")
        return 0
    if config.verbose and not config.quiet:
        print("[Nightrider] Max rounds reached or loop stopped before passing. See agent_logs/ for details.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
