import shlex
import subprocess
from dataclasses import dataclass

@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False

def run_command(command: str, timeout: int = 60) -> CommandResult:
    try:
        args = shlex.split(command)

        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )

        return CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "timeout",
            timed_out=True,
        )

    except FileNotFoundError as exc:
        return CommandResult(
            returncode=127,
            stdout="",
            stderr=str(exc),
        )
