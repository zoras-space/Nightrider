"""Timestamped log helpers for Nightrider compliance evidence."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


REQUIRED_LOG_FILES = (
    "prompts.log",
    "decisions.log",
    "commands.log",
    "test_runs.log",
    "errors.log",
    "human_interventions.log",
    "final_report.md",
)

LOG_DIR = Path("agent_logs")
NO_INTERVENTIONS_TEXT = "No human interventions logged yet."


def timestamp() -> str:
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def ensure_log_files(log_dir: Path = LOG_DIR) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    for filename in REQUIRED_LOG_FILES:
        path = log_dir / filename
        if not path.exists():
            if filename == "human_interventions.log":
                path.write_text(f"{NO_INTERVENTIONS_TEXT}\n", encoding="utf-8")
            elif filename == "final_report.md":
                path.write_text("# Nightrider Final Report\n\nNo run completed yet.\n", encoding="utf-8")
            else:
                path.write_text("", encoding="utf-8")


def append_log(filename: str, label: str, text: str, log_dir: Path = LOG_DIR) -> None:
    ensure_log_files(log_dir)
    path = log_dir / filename
    clean_text = text.rstrip()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp()} {label}\n")
        if clean_text:
            handle.write(f"{clean_text}\n")
        handle.write("\n")


def log_prompt(text: str) -> None:
    append_log("prompts.log", "PROMPT", text)


def log_decision(text: str) -> None:
    append_log("decisions.log", "DECISION", text)


def log_command(command: str, exit_code: int, stdout: str, stderr: str, duration: float) -> None:
    body = (
        f"command: {command}\n"
        f"exit_code: {exit_code}\n"
        f"duration_seconds: {duration:.3f}\n"
        f"stdout:\n{stdout.rstrip() or '<empty>'}\n"
        f"stderr:\n{stderr.rstrip() or '<empty>'}"
    )
    append_log("commands.log", "COMMAND", body)


def log_test_run(round_number: int, exit_code: int, stdout: str, stderr: str) -> None:
    body = (
        f"round: {round_number}\n"
        f"exit_code: {exit_code}\n"
        f"stdout:\n{stdout.rstrip() or '<empty>'}\n"
        f"stderr:\n{stderr.rstrip() or '<empty>'}"
    )
    append_log("test_runs.log", "TEST_RUN", body)


def log_error(text: str) -> None:
    append_log("errors.log", "ERROR", text)


def log_human_intervention(text: str) -> None:
    ensure_log_files(LOG_DIR)
    path = LOG_DIR / "human_interventions.log"
    current = path.read_text(encoding="utf-8")
    if current.strip() == NO_INTERVENTIONS_TEXT:
        path.write_text("", encoding="utf-8")
    append_log("human_interventions.log", "HUMAN_INTERVENTION", text)

