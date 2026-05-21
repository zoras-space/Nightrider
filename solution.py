#!/usr/bin/env python3
"""
solution.py — Competition entry point
======================================

ARCHITECTURE (top to bottom):
  1. read_input()    — reads from stdin or --input file
  2. parse_input()   — turns raw text into a structured Python object
  3. solve()         — YOUR LOGIC GOES HERE (replace this when spec drops)
  4. format_output() — turns the result into a printable string
  5. write_output()  — prints to stdout or writes to --output file

Flow:
  stdin/file
      └─► read_input()
              └─► parse_input()  →  (data, is_json)
                      └─► solve()
                              └─► format_output()
                                      └─► write_output()  →  stdout/file

Exit codes:
  0 = success
  1 = bad input (empty or unreadable)
  2 = input file not found
  3 = unexpected crash
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────
# LOGGING  (stderr only — never pollutes stdout)
# ─────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stderr,
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# STEP 1 — READ
# ─────────────────────────────────────────────
def read_input(path: str | None) -> str:
    """Return raw text from a file or stdin."""
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


# ─────────────────────────────────────────────
# STEP 2 — PARSE
# Returns (parsed_value, was_json).
# Replace this if the spec uses CSV, XML, a custom format, etc.
# ─────────────────────────────────────────────
def parse_input(raw: str) -> tuple[Any, bool]:
    raw = raw.strip()
    if not raw:
        raise ValueError("Empty input")

    try:
        return json.loads(raw), True   # valid JSON of any kind
    except json.JSONDecodeError:
        return raw, False              # plain text


# ─────────────────────────────────────────────
# STEP 3 — SOLVE  ← REPLACE THIS WHEN SPEC DROPS
#
# Args:
#   data    — parsed value (dict, list, str, int, bool, None, …)
#   is_json — True if the original input was JSON
#
# Return any JSON-serialisable value or a plain string.
# ─────────────────────────────────────────────
def solve(data: Any, is_json: bool) -> Any:

    # ── STUB ──────────────────────────────────
    if not is_json:
        return data                           # plain text → echo back
    return {"status": "ok", "result": data}  # any JSON → wrap in envelope
    # ── END STUB ──────────────────────────────


# ─────────────────────────────────────────────
# STEP 4 — FORMAT
# ─────────────────────────────────────────────
def format_output(result: Any) -> str:
    if isinstance(result, str):
        return result
    return json.dumps(result, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────
# STEP 5 — WRITE
# ─────────────────────────────────────────────
def write_output(result: Any, path: str | None) -> None:
    text = format_output(result)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


# ─────────────────────────────────────────────
# COMPAT SHIM — tests import process() by name
# ─────────────────────────────────────────────
def process(raw: str) -> Any:
    data, is_json = parse_input(raw)
    return solve(data, is_json)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Competition solution",
        epilog='Example:  echo \'{"x": 1}\' | python3 solution.py',
    )
    p.add_argument("--input",   "-i", metavar="FILE", help="Read from FILE (default: stdin)")
    p.add_argument("--output",  "-o", metavar="FILE", help="Write to FILE (default: stdout)")
    p.add_argument("--verbose", "-v", action="store_true", help="Debug logging to stderr")
    return p


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main(argv: list | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        log.setLevel(logging.DEBUG)

    try:
        raw = read_input(args.input)
        log.debug("Read %d chars", len(raw))

        data, is_json = parse_input(raw)
        log.debug("Parsed (is_json=%s): %r", is_json, data)

        result = solve(data, is_json)
        log.debug("Result: %r", result)

        write_output(result, args.output)
        return 0

    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    except FileNotFoundError as exc:
        print(f"ERROR: file not found — {exc}", file=sys.stderr)
        return 2

    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        log.debug("Traceback:", exc_info=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())