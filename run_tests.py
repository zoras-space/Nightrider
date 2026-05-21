#!/usr/bin/env python3
"""
Public test runner — mirrors what secret_spec/test_runner/run_tests.py will do.

Usage:
    python3 secret_spec/test_runner/run_tests.py --program "python3 solution.py" --suite public
    python3 secret_spec/test_runner/run_tests.py --program "python3 solution.py" --suite all
    python3 secret_spec/test_runner/run_tests.py --program "python3 solution.py" --suite public --verbose
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Test case definition
# ---------------------------------------------------------------------------
@dataclass
class TestCase:
    name: str
    stdin: str
    expected_output: str           # exact stdout expected (stripped)
    expected_exit_code: int = 0
    tags: list = field(default_factory=list)
    points: int = 10
    suite: str = "public"          # "public" | "hidden"


# ---------------------------------------------------------------------------
# Public test suite — add cases here as you learn the spec
# ---------------------------------------------------------------------------
PUBLIC_TESTS: list[TestCase] = [
    # ---- Smoke tests ----
    TestCase(
        name="empty_json_object",
        stdin='{}',
        expected_output='{\n  "status": "ok",\n  "result": {}\n}',
        tags=["smoke", "json"],
    ),
    TestCase(
        name="json_string_value",
        stdin='"hello"',
        expected_output='{\n  "status": "ok",\n  "result": "hello"\n}',
        tags=["smoke", "json"],
    ),
    TestCase(
        name="json_number",
        stdin='42',
        expected_output='{\n  "status": "ok",\n  "result": 42\n}',
        tags=["smoke", "json"],
    ),
    TestCase(
        name="json_array",
        stdin='[1, 2, 3]',
        expected_output='{\n  "status": "ok",\n  "result": [\n    1,\n    2,\n    3\n  ]\n}',
        tags=["json", "array"],
    ),
    # ---- Plain text fallback ----
    TestCase(
        name="plain_text_passthrough",
        stdin="hello world",
        expected_output="hello world",
        tags=["text"],
    ),
    TestCase(
        name="plain_text_multiline",
        stdin="line one\nline two",
        expected_output="line one\nline two",
        tags=["text"],
    ),
    # ---- Error cases ----
    TestCase(
        name="empty_input_exits_nonzero",
        stdin="",
        expected_output="",          # stderr is not checked by default
        expected_exit_code=1,
        tags=["error", "edge"],
    ),
    TestCase(
        name="whitespace_only_exits_nonzero",
        stdin="   \n  \t  ",
        expected_output="",
        expected_exit_code=1,
        tags=["error", "edge"],
    ),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
@dataclass
class Result:
    test: TestCase
    passed: bool
    actual_output: str
    actual_exit_code: int
    duration_ms: float
    error: Optional[str] = None


def run_one(test: TestCase, program: str, timeout: int = 10) -> Result:
    cmd = program.split()
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            input=test.stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return Result(
            test=test,
            passed=False,
            actual_output="",
            actual_exit_code=-1,
            duration_ms=(time.monotonic() - t0) * 1000,
            error=f"TIMEOUT after {timeout}s",
        )
    except Exception as exc:
        return Result(
            test=test,
            passed=False,
            actual_output="",
            actual_exit_code=-1,
            duration_ms=(time.monotonic() - t0) * 1000,
            error=str(exc),
        )

    duration_ms = (time.monotonic() - t0) * 1000
    actual = proc.stdout.strip()
    expected = test.expected_output.strip()

    # For error cases we only check exit code, not output
    if test.expected_exit_code != 0:
        passed = proc.returncode == test.expected_exit_code
    else:
        passed = (actual == expected) and (proc.returncode == test.expected_exit_code)

    return Result(
        test=test,
        passed=passed,
        actual_output=actual,
        actual_exit_code=proc.returncode,
        duration_ms=duration_ms,
    )


def run_suite(
    tests: list[TestCase],
    program: str,
    verbose: bool = False,
    suite_filter: str = "public",
) -> tuple[int, int]:
    if suite_filter != "all":
        tests = [t for t in tests if t.suite == suite_filter]

    total_points = sum(t.points for t in tests)
    earned_points = 0
    passed = 0

    print(f"\n{'='*60}")
    print(f"  Running {len(tests)} tests  [{suite_filter} suite]")
    print(f"  Program: {program}")
    print(f"{'='*60}\n")

    for test in tests:
        result = run_one(test, program)
        status = "✓ PASS" if result.passed else "✗ FAIL"
        tags = " ".join(f"[{t}]" for t in test.tags)
        print(f"  {status}  {test.name:<45} {result.duration_ms:6.1f}ms  {tags}")

        if result.passed:
            passed += 1
            earned_points += test.points
        elif verbose:
            print(f"         Expected exit: {test.expected_exit_code}  Got: {result.actual_exit_code}")
            if test.expected_exit_code == 0:
                print(f"         Expected stdout:\n{_indent(test.expected_output)}")
                print(f"         Actual stdout:\n{_indent(result.actual_output)}")
            if result.error:
                print(f"         Error: {result.error}")

    print(f"\n{'='*60}")
    print(f"  Score: {earned_points}/{total_points}  ({passed}/{len(tests)} tests passed)")
    print(f"{'='*60}\n")

    return earned_points, total_points


def _indent(text: str, prefix: str = "           ") -> str:
    return "\n".join(prefix + line for line in text.splitlines()) or f"{prefix}(empty)"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Competition test runner")
    p.add_argument("--program", required=True, help='Program to test, e.g. "python3 solution.py"')
    p.add_argument("--suite", default="public", choices=["public", "hidden", "all"])
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    earned, total = run_suite(PUBLIC_TESTS, args.program, args.verbose, args.suite)
    sys.exit(0 if earned == total else 1)


if __name__ == "__main__":
    main()
