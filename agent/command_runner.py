"""Subprocess execution with clear capture for the Night Drive Loop."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timed_out: bool


def run_command(command: str, timeout_seconds: int = 60) -> CommandResult:
    """Run a shell command and capture its observable behavior."""

    start = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            shell=True,
            timeout=timeout_seconds,
            text=True,
            capture_output=True,
        )
        duration = time.monotonic() - start
        return CommandResult(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration=duration,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - start
        return CommandResult(
            command=command,
            exit_code=124,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + f"\nTimed out after {timeout_seconds} seconds.",
            duration=duration,
            timed_out=True,
        )

