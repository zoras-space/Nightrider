import json, subprocess, sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from solution import process, read_input, write_output


class TestProcessJSON:
    def test_empty_object(self):      assert process("{}") == {"status": "ok", "result": {}}

    def test_nested_object(self):     assert process('{"k":"v"}')["result"]["k"] == "v"

    def test_json_array(self):        assert process("[1,2,3]")["result"] == [1, 2, 3]

    def test_json_number(self):       assert process("42")["result"] == 42

    def test_json_string(self):       assert process('"hi"')["result"] == "hi"  # JSON string → wrapped

    def test_json_null(self):         assert process("null")["result"] is None

    def test_json_bool_true(self):    assert process("true")["result"] is True

    def test_json_bool_false(self):   assert process("false")["result"] is False


class TestProcessText:
    def test_plain_text(self):        assert process("hello world") == "hello world"

    def test_multiline(self):         assert process("a\nb") == "a\nb"

    def test_strips_whitespace(self): assert process("  hi  ") == "hi"


class TestProcessErrors:
    def test_empty_raises(self):      pytest.raises(ValueError, process, "")

    def test_whitespace_raises(self): pytest.raises(ValueError, process, "   ")


def run(stdin):
    p = subprocess.run(
        [sys.executable, "solution.py"],
        input=stdin, capture_output=True, text=True,
        cwd=Path(__file__).parent.parent,
    )
    return p.returncode, p.stdout.strip()


class TestMainReturnCodes:
    def test_json_exits_zero(self):    assert run('{"x":1}')[0] == 0

    def test_text_exits_zero(self):    assert run("hello")[0] == 0

    def test_empty_exits_one(self):    assert run("")[0] == 1

    def test_spaces_exits_one(self):   assert run("   ")[0] == 1


class TestMainOutput:
    def test_json_is_valid(self):      assert json.loads(run('{"a":1}')[1])["status"] == "ok"

    def test_text_passthrough(self):   assert run("hello")[1] == "hello"

    def test_number_wrapped(self):     assert json.loads(run("99")[1])["result"] == 99


class TestFileIO:
    def test_read_file(self, tmp_path):
        f = tmp_path / "in.txt";
        f.write_text("hi")
        assert read_input(str(f)) == "hi"

    def test_write_string(self, tmp_path):
        f = tmp_path / "out.txt";
        write_output("hello", str(f))
        assert f.read_text().strip() == "hello"

    def test_write_dict(self, tmp_path):
        f = tmp_path / "out.json";
        write_output({"a": 1}, str(f))
        assert json.loads(f.read_text())["a"] == 1

    def test_missing_file_raises(self):
        pytest.raises(FileNotFoundError, read_input, "/no/such/file.txt")


class TestVerboseFlag:
    def test_verbose_still_produces_stdout(self):
        p = subprocess.run(
            [sys.executable, "solution.py", "--verbose"],
            input='{"v":true}', capture_output=True, text=True,
            cwd=Path(__file__).parent.parent,
        )
        assert p.returncode == 0
        assert json.loads(p.stdout)["status"] == "ok"
