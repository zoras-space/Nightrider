from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROGRAM = [sys.executable, "workspace/solution.py"]


def run_program(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(PROGRAM + list(args), text=True, capture_output=True)


def parse_json_stdout(stdout: str) -> dict[str, int]:
    assert stdout.strip(), "program should print JSON to stdout on success"
    assert "debug" not in stdout.lower()
    assert "trace" not in stdout.lower()
    parsed = json.loads(stdout)
    assert set(parsed) == {"line_count", "word_count", "char_count"}
    assert all(isinstance(value, int) for value in parsed.values())
    return parsed


def test_counts_unicode_tabs_blank_lines_and_final_no_newline(tmp_path: Path) -> None:
    sample = tmp_path / "mixed.txt"
    content = "alpha\tbeta\n\ncafe Ωmega"
    sample.write_text(content, encoding="utf-8")

    result = run_program(str(sample))

    assert result.returncode == 0
    assert result.stderr == ""
    assert parse_json_stdout(result.stdout) == {
        "line_count": 3,
        "word_count": 4,
        "char_count": len(content),
    }


def test_counts_trailing_newline_characters(tmp_path: Path) -> None:
    sample = tmp_path / "trailing.txt"
    content = "one\n\n"
    sample.write_text(content, encoding="utf-8")

    result = run_program(str(sample))

    assert result.returncode == 0
    assert result.stderr == ""
    assert parse_json_stdout(result.stdout) == {
        "line_count": 2,
        "word_count": 1,
        "char_count": 5,
    }


def test_rejects_extra_argument_without_stdout(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("hello\n", encoding="utf-8")

    result = run_program(str(sample), "extra")

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()


def test_rejects_directory_path_without_stdout(tmp_path: Path) -> None:
    result = run_program(str(tmp_path))

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()


def test_output_is_single_json_value(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("a b c\n", encoding="utf-8")

    result = run_program(str(sample))

    assert result.returncode == 0
    assert result.stdout.count("{") == 1
    assert result.stdout.count("}") == 1
    parse_json_stdout(result.stdout)
