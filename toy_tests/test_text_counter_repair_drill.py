from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROGRAM = [sys.executable, "workspace/solution.py"]


def run_program(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(PROGRAM + list(args), text=True, capture_output=True)


def test_requires_nonempty_line_count_field(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("alpha beta\n\n gamma \n", encoding="utf-8")

    result = run_program(str(sample))

    assert result.returncode == 0
    assert result.stderr == ""
    parsed = json.loads(result.stdout)
    assert parsed == {
        "line_count": 3,
        "word_count": 3,
        "char_count": 20,
        "nonempty_line_count": 2,
    }


def test_empty_file_has_zero_nonempty_lines(tmp_path: Path) -> None:
    sample = tmp_path / "empty.txt"
    sample.write_text("", encoding="utf-8")

    result = run_program(str(sample))

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "line_count": 0,
        "word_count": 0,
        "char_count": 0,
        "nonempty_line_count": 0,
    }


def test_whitespace_only_lines_are_not_nonempty(tmp_path: Path) -> None:
    sample = tmp_path / "spaces.txt"
    sample.write_text("   \n\t\nword\n", encoding="utf-8")

    result = run_program(str(sample))

    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["line_count"] == 3
    assert parsed["word_count"] == 1
    assert parsed["char_count"] == 11
    assert parsed["nonempty_line_count"] == 1


def test_error_stays_on_stderr_for_missing_file(tmp_path: Path) -> None:
    result = run_program(str(tmp_path / "missing.txt"))

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()
