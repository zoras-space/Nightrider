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


def test_normalizes_json_objects(tmp_path: Path) -> None:
    source = tmp_path / "items.json"
    source.write_text(
        json.dumps(
            [
                {"id": 2, "name": "  Ada  ", "active": True, "ignored": "x"},
                {"id": 3, "name": "Linus"},
            ]
        ),
        encoding="utf-8",
    )

    result = run_program(str(source))

    assert result.returncode == 0
    assert result.stderr == ""
    assert assert_json_only_stdout(result.stdout) == [
        {"id": 2, "name": "Ada", "active": True},
        {"id": 3, "name": "Linus", "active": False},
    ]


def test_invalid_json_is_error(tmp_path: Path) -> None:
    source = tmp_path / "broken.json"
    source.write_text("{not json", encoding="utf-8")

    result = run_program(str(source))

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()


def test_root_must_be_array(tmp_path: Path) -> None:
    source = tmp_path / "object.json"
    source.write_text(json.dumps({"id": 1, "name": "Ada"}), encoding="utf-8")

    result = run_program(str(source))

    assert result.returncode != 0
    assert result.stdout == ""
    assert "array" in result.stderr.lower()


def test_missing_required_field_is_error(tmp_path: Path) -> None:
    source = tmp_path / "missing.json"
    source.write_text(json.dumps([{"id": 1}]), encoding="utf-8")

    result = run_program(str(source))

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()
