"""Configuration defaults for the Nightrider agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_MODEL = "qwen2.5-coder:7b"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_LOG_DIR = Path("agent_logs")
DEFAULT_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class AgentConfig:
    """Runtime settings for one Night Drive Loop."""

    spec_path: Path
    program_path: Path
    test_command: str
    max_rounds: int
    model: str
    log_dir: Path = DEFAULT_LOG_DIR
    ollama_url: str = DEFAULT_OLLAMA_URL
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    verbose: bool = False
    quiet: bool = False


def resolve_model(cli_model: str | None) -> str:
    """Pick the model from CLI, environment, then local default."""

    return cli_model or os.environ.get("AGENT_MODEL") or DEFAULT_MODEL
