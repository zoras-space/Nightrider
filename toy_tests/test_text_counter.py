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
    assert "error" not in stdout.lower()
    return parsed


def test_counts_text_file(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("one two\nthree\n", encoding="utf-8")

    result = run_program(str(sample))

    assert result.returncode == 0
    assert result.stderr == ""
    assert assert_json_only_stdout(result.stdout) == {
        "line_count": 2,
        "word_count": 3,
        "char_count": 14,
    }


def test_empty_file(tmp_path: Path) -> None:
    sample = tmp_path / "empty.txt"
    sample.write_text("", encoding="utf-8")

    result = run_program(str(sample))

    assert result.returncode == 0
    assert assert_json_only_stdout(result.stdout) == {
        "line_count": 0,
        "word_count": 0,
        "char_count": 0,
    }


def test_missing_argument_is_error() -> None:
    result = run_program()

    assert result.returncode != 0
    assert result.stdout == ""
    assert "usage" in result.stderr.lower() or "argument" in result.stderr.lower()


def test_missing_file_is_error(tmp_path: Path) -> None:
    result = run_program(str(tmp_path / "missing.txt"))

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()
