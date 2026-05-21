from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROGRAM = [sys.executable, "workspace/solution.py"]


def run_program(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(PROGRAM + list(args), text=True, capture_output=True)


def assert_json_only_stdout(stdout: str) -> object:
    parsed = json.loads(stdout)
    assert "debug" not in stdout.lower()
    assert "trace" not in stdout.lower()
    return parsed


def test_inventory_commands(tmp_path: Path) -> None:
    commands = tmp_path / "commands.txt"
    commands.write_text(
        "\n".join(
            [
                "ADD apple 5",
                "ADD banana 2",
                "TOTAL",
                "REMOVE apple 3",
                "TOTAL",
            ]
        ),
        encoding="utf-8",
    )

    result = run_program(str(commands))

    assert result.returncode == 0
    assert result.stderr == ""
    assert assert_json_only_stdout(result.stdout) == {
        "inventory": {"apple": 2, "banana": 2},
        "totals": [7, 4],
    }


def test_zero_quantity_items_are_omitted(tmp_path: Path) -> None:
    commands = tmp_path / "commands.txt"
    commands.write_text("ADD lamp 1\nREMOVE lamp 1\nTOTAL\n", encoding="utf-8")

    result = run_program(str(commands))

    assert result.returncode == 0
    assert assert_json_only_stdout(result.stdout) == {"inventory": {}, "totals": [0]}


def test_remove_too_many_is_error(tmp_path: Path) -> None:
    commands = tmp_path / "commands.txt"
    commands.write_text("ADD apple 1\nREMOVE apple 2\n", encoding="utf-8")

    result = run_program(str(commands))

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()


def test_malformed_command_is_error(tmp_path: Path) -> None:
    commands = tmp_path / "commands.txt"
    commands.write_text("ADD apple\n", encoding="utf-8")

    result = run_program(str(commands))

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()
