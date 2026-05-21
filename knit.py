#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path


def compile_command(input_file: str) -> int:
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: input file not found: {input_file}")
        return 1

    command = [
        "python3",
        "agent/run_agent.py",
        "--spec",
        str(input_path),
        "--program",
        "workspace/solution.py",
        "--test-command",
        "pytest -q",
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