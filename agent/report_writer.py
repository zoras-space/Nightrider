"""Final report creation for the Nightrider run."""

from __future__ import annotations

from pathlib import Path

from agent import logger
from agent.model_client import OllamaClient
from agent.prompts import FINAL_REPORT_PROMPT


def write_final_report(
    client: OllamaClient,
    run_context: str,
    log_dir: Path = Path("agent_logs"),
) -> None:
    prompt = FINAL_REPORT_PROMPT.format(run_context=run_context)
    logger.log_prompt(prompt)
    try:
        response = client.generate(prompt)
        report = response.text.strip()
    except Exception as exc:  # noqa: BLE001
        logger.log_error(f"Final report model generation failed: {exc}")
        report = f"# Nightrider Final Report\n\n{run_context}\n"
    logger.ensure_log_files(log_dir)
    (log_dir / "final_report.md").write_text(report + "\n", encoding="utf-8")

