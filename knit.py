#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path


DEFAULT_TESTS = {
    "text_counter_spec.md": "pytest toy_tests/test_text_counter.py -q",
    "json_transformer_spec.md": "pytest toy_tests/test_json_transformer.py -q",
    "inventory_cli_spec.md": "pytest toy_tests/test_inventory_cli.py -q",
}


def resolve_test_command(spec_path: Path) -> str:
    return DEFAULT_TESTS.get(spec_path.name, "pytest -q")


def compile_command(input_file: str) -> int:
    spec_path = Path(input_file)

    if not spec_path.exists():
        print(f"Error: input file not found: {input_file}")
        return 1

    test_command = resolve_test_command(spec_path)

    command = [
        "python3",
        "agent/run_agent.py",
        "--spec",
        str(spec_path),
        "--program",
        "workspace/solution.py",
        "--test-command",
        test_command,
        "--max-rounds",
        "5",
    ]

    return subprocess.call(command)


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 knit.py compile <input_file>")
        return 1

    command = sys.argv[1]

    if command == "compile":
        return compile_command(sys.argv[2])

    print(f"Unknown command: {command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())