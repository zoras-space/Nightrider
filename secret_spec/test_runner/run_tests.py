#!/usr/bin/env python3
import argparse, json, subprocess, sys, time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TestCase:
    name: str
    stdin: str
    expected_output: str
    expected_exit_code: int = 0
    tags: list = field(default_factory=list)
    points: int = 10
    suite: str = "public"

@dataclass
class Result:
    test: TestCase
    passed: bool
    actual_output: str
    actual_exit_code: int
    duration_ms: float
    error: Optional[str] = None

PUBLIC_TESTS = [
    TestCase("empty_json_object", '{}', '{\n  "status": "ok",\n  "result": {}\n}', tags=["smoke","json"]),
    TestCase("json_string_value", '"hello"', '{\n  "status": "ok",\n  "result": "hello"\n}', tags=["smoke","json"]),
    TestCase("json_number", '42', '{\n  "status": "ok",\n  "result": 42\n}', tags=["smoke","json"]),
    TestCase("json_array", '[1, 2, 3]', '{\n  "status": "ok",\n  "result": [\n    1,\n    2,\n    3\n  ]\n}', tags=["json","array"]),
    TestCase("plain_text_passthrough", "hello world", "hello world", tags=["text"]),
    TestCase("plain_text_multiline", "line one\nline two", "line one\nline two", tags=["text"]),
    TestCase("empty_input_exits_nonzero", "", "", expected_exit_code=1, tags=["error","edge"]),
    TestCase("whitespace_only_exits_nonzero", "   \n  ", "", expected_exit_code=1, tags=["error","edge"]),
]

def run_one(test, program, timeout=10):
    t0 = time.monotonic()
    try:
        proc = subprocess.run(program.split(), input=test.stdin, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return Result(test, False, "", -1, (time.monotonic()-t0)*1000, f"TIMEOUT after {timeout}s")
    except Exception as exc:
        return Result(test, False, "", -1, (time.monotonic()-t0)*1000, str(exc))
    duration_ms = (time.monotonic()-t0)*1000
    actual = proc.stdout.strip()
    expected = test.expected_output.strip()
    passed = (proc.returncode == test.expected_exit_code) if test.expected_exit_code != 0 else (actual == expected and proc.returncode == 0)
    return Result(test, passed, actual, proc.returncode, duration_ms)

def run_suite(tests, program, verbose=False, suite_filter="public"):
    if suite_filter != "all":
        tests = [t for t in tests if t.suite == suite_filter]
    total_points = sum(t.points for t in tests)
    earned, passed = 0, 0
    print(f"\n{'='*60}\n  Running {len(tests)} tests  [{suite_filter} suite]\n  Program: {program}\n{'='*60}\n")
    for test in tests:
        result = run_one(test, program)
        status = "✓ PASS" if result.passed else "✗ FAIL"
        tags = " ".join(f"[{t}]" for t in test.tags)
        print(f"  {status}  {test.name:<45} {result.duration_ms:6.1f}ms  {tags}")
        if result.passed:
            passed += 1
            earned += test.points
        elif verbose:
            print(f"         Expected exit: {test.expected_exit_code}  Got: {result.actual_exit_code}")
            if test.expected_exit_code == 0:
                print(f"         Expected: {repr(test.expected_output.strip())}")
                print(f"         Actual:   {repr(result.actual_output)}")
            if result.error:
                print(f"         Error: {result.error}")
    print(f"\n{'='*60}\n  Score: {earned}/{total_points}  ({passed}/{len(tests)} tests passed)\n{'='*60}\n")
    return earned, total_points

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--program", required=True)
    p.add_argument("--suite", default="public", choices=["public","hidden","all"])
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    earned, total = run_suite(PUBLIC_TESTS, args.program, args.verbose, args.suite)
    sys.exit(0 if earned == total else 1)

if __name__ == "__main__":
    main()
