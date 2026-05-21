"""
tests/test_solution.py — unit tests for solution internals.
Run with:  python3 -m pytest tests/ -v
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Make sure the repo root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
from solution import process, read_input, write_output, main

# ---------------------------------------------------------------------------
# process() — core logic
# ---------------------------------------------------------------------------
class TestProcessJSON:
    def test_empty_object(self):
        result = process("{}")
        assert result == {"status": "ok", "result": {}}

    def test_nested_object(self):
        result = process('{"key": "value", "num": 42}')
        assert result["status"] == "ok"
        assert result["result"]["key"] == "value"

    def test_json_array(self):
        result = process("[1, 2, 3]")
        assert result["result"] == [1, 2, 3]

    def test_json_number(self):
        result = process("42")
        assert result["result"] == 42

    def test_json_string(self):
        result = process('"hello"')
        assert result["result"] == "hello"

    def test_json_null(self):
        result = process("null")
        assert result["result"] is None

    def test_json_boolean_true(self):
        result = process("true")
        assert result["result"] is True

    def test_json_boolean_false(self):
        result = process("false")
        assert result["result"] is False


class TestProcessText:
    def test_plain_text_passthrough(self):
        result = process("hello world")
        assert result == "hello world"

    def test_multiline_text(self):
        result = process("line one\nline two")
        assert result == "line one\nline two"

    def test_strips_trailing_whitespace(self):
        # process() strips input, so leading/trailing whitespace is removed
        result = process("  hello  ")
        assert result == "hello"


class TestProcessErrors:
    def test_empty_input_raises(self):
        with pytest.raises(ValueError, match="Empty input"):
            process("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="Empty input"):
            process("   \n\t  ")


# ---------------------------------------------------------------------------
# main() — integration via return code
# ---------------------------------------------------------------------------
class TestMainReturnCodes:
    def _run(self, stdin_text: str) -> tuple[int, str]:
        """Run main() via subprocess and return (exit_code, stdout)."""
        proc = subprocess.run(
            [sys.executable, "solution.py"],
            input=stdin_text,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        return proc.returncode, proc.stdout.strip()

    def test_valid_json_exits_zero(self):
        code, _ = self._run('{"x": 1}')
        assert code == 0

    def test_plain_text_exits_zero(self):
        code, _ = self._run("some text")
        assert code == 0

    def test_empty_input_exits_one(self):
        code, _ = self._run("")
        assert code == 1

    def test_whitespace_exits_one(self):
        code, _ = self._run("   ")
        assert code == 1


class TestMainOutput:
    def _stdout(self, stdin_text: str) -> str:
        proc = subprocess.run(
            [sys.executable, "solution.py"],
            input=stdin_text,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        return proc.stdout.strip()

    def test_json_output_is_valid_json(self):
        raw = self._stdout('{"a": 1}')
        parsed = json.loads(raw)          # must not raise
        assert parsed["status"] == "ok"

    def test_plain_text_output_is_text(self):
        raw = self._stdout("hello")
        assert raw == "hello"

    def test_number_wrapped_in_status(self):
        raw = self._stdout("99")
        parsed = json.loads(raw)
        assert parsed["result"] == 99


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------
class TestFileIO:
    def test_read_input_from_file(self, tmp_path):
        f = tmp_path / "in.txt"
        f.write_text("file content", encoding="utf-8")
        assert read_input(str(f)) == "file content"

    def test_write_output_string_to_file(self, tmp_path):
        f = tmp_path / "out.txt"
        write_output("hello", str(f))
        assert f.read_text().strip() == "hello"

    def test_write_output_dict_to_file(self, tmp_path):
        f = tmp_path / "out.json"
        write_output({"a": 1}, str(f))
        parsed = json.loads(f.read_text())
        assert parsed["a"] == 1

    def test_missing_input_file_raises(self):
        with pytest.raises(FileNotFoundError):
            read_input("/nonexistent/path/file.txt")


# ---------------------------------------------------------------------------
# CLI flag: --verbose doesn't break output
# ---------------------------------------------------------------------------
class TestVerboseFlag:
    def test_verbose_still_produces_stdout(self):
        proc = subprocess.run(
            [sys.executable, "solution.py", "--verbose"],
            input='{"v": true}',
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        assert proc.returncode == 0
        parsed = json.loads(proc.stdout)
        assert parsed["status"] == "ok"
