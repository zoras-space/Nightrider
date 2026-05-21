#!/usr/bin/env python3
"""
solution.py — Competition entry point
======================================

ARCHITECTURE:
  read_input() → parse_input() → solve() → format_output() → write_output()

The agent rewrites ONLY solve() (and parse_input() if the format changes).
Everything else is stable infrastructure.

Exit codes:  0=success  1=bad input  2=file not found  3=unexpected crash
"""

import sys
import json
import re
import argparse
import logging
from pathlib import Path
from typing import Any

logging.basicConfig(stream=sys.stderr, level=logging.WARNING,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# STEP 1 — READ
# ──────────────────────────────────────────────
def read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


# ──────────────────────────────────────────────
# STEP 2 — PARSE
# Detects format and returns (data, format_tag).
# format_tag: "json" | "csv" | "lines" | "text"
# Replace/extend this when the spec format is known.
# ──────────────────────────────────────────────
def parse_input(raw: str) -> tuple[Any, str]:
    raw = raw.strip()
    if not raw:
        raise ValueError("Empty input")

    # JSON
    try:
        return json.loads(raw), "json"
    except json.JSONDecodeError:
        pass

    # CSV-like (header row + data rows, comma or tab separated)
    lines = raw.splitlines()
    if len(lines) >= 2 and ("," in lines[0] or "\t" in lines[0]):
        sep = "\t" if "\t" in lines[0] else ","
        headers = [h.strip() for h in lines[0].split(sep)]
        rows = []
        for line in lines[1:]:
            if line.strip():
                values = [v.strip() for v in line.split(sep)]
                rows.append(dict(zip(headers, values)))
        if rows:
            return {"headers": headers, "rows": rows}, "csv"

    # Multiple lines → list
    if len(lines) > 1:
        return [l.strip() for l in lines if l.strip()], "lines"

    # Single line → plain string
    return raw, "text"


# ──────────────────────────────────────────────
# STEP 3 — SOLVE  ← AGENT REWRITES THIS
#
# This is a CAPABLE STUB. It handles common competition
# patterns so the agent has a working baseline to patch,
# rather than starting from nothing.
#
# Common patterns pre-wired:
#   - JSON transformation / filtering / aggregation
#   - Line processing (sort, filter, count, transform)
#   - CSV aggregation (sum, average, group-by)
#   - String operations (reverse, count, parse)
#   - Arithmetic / numeric tasks
#
# When the spec drops: the agent replaces the body of
# this function. parse_input() and format_output() only
# change if the I/O format changes.
# ──────────────────────────────────────────────
def solve(data: Any, fmt: str) -> Any:
    # ── JSON input ────────────────────────────
    if fmt == "json":
        return _solve_json(data)

    # ── CSV input ─────────────────────────────
    if fmt == "csv":
        return _solve_csv(data)

    # ── Multiple lines ────────────────────────
    if fmt == "lines":
        return _solve_lines(data)

    # ── Single string / plain text ────────────
    return _solve_text(data)


# ── JSON handler ──────────────────────────────
def _solve_json(data: Any) -> Any:
    """
    Handles structured JSON input.
    Stub: wraps in status envelope.
    Agent replaces this with spec logic.
    """
    return {"status": "ok", "result": data}


# ── CSV handler ───────────────────────────────
def _solve_csv(data: dict) -> Any:
    """
    Handles tabular input.
    Stub: returns row count summary.
    Agent replaces with spec logic (filter, sum, group-by, etc.)
    """
    rows = data.get("rows", [])
    return {"row_count": len(rows), "rows": rows}


# ── Lines handler ─────────────────────────────
def _solve_lines(lines: list[str]) -> Any:
    """
    Handles multi-line text input.
    Stub: returns lines as-is.
    Agent replaces with spec logic (sort, filter, transform, etc.)
    """
    return "\n".join(lines)


# ── Text handler ──────────────────────────────
def _solve_text(text: str) -> str:
    """
    Handles single-line / plain text.
    Stub: echo back.
    Agent replaces with spec logic.
    """
    return text


# ── Utility functions the agent can call from solve() ──
def to_int(s: Any, default: int = 0) -> int:
    """Safe int conversion."""
    try:
        return int(str(s).strip())
    except (ValueError, TypeError):
        return default


def to_float(s: Any, default: float = 0.0) -> float:
    """Safe float conversion."""
    try:
        return float(str(s).strip())
    except (ValueError, TypeError):
        return default


def flatten(nested: list) -> list:
    """Flatten one level of nesting."""
    out = []
    for item in nested:
        if isinstance(item, list):
            out.extend(item)
        else:
            out.append(item)
    return out


def group_by(rows: list[dict], key: str) -> dict[str, list]:
    """Group list of dicts by a key."""
    groups: dict[str, list] = {}
    for row in rows:
        k = str(row.get(key, ""))
        groups.setdefault(k, []).append(row)
    return groups


def extract_numbers(text: str) -> list[float]:
    """Pull all numbers out of a string."""
    return [float(x) for x in re.findall(r"-?\d+\.?\d*", text)]


# ──────────────────────────────────────────────
# STEP 4 — FORMAT
# ──────────────────────────────────────────────
def format_output(result: Any) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, (int, float, bool)) and not isinstance(result, bool):
        return str(result)
    return json.dumps(result, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────────
# STEP 5 — WRITE
# ──────────────────────────────────────────────
def write_output(result: Any, path: str | None) -> None:
    text = format_output(result)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


# ──────────────────────────────────────────────
# COMPAT SHIM — tests import process() by name
# ──────────────────────────────────────────────
def process(raw: str) -> Any:
    data, fmt = parse_input(raw)
    return solve(data, fmt)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Competition solution",
        epilog='Example:  echo \'{"x": 1}\' | python3 solution.py',
    )
    p.add_argument("--input", "-i", metavar="FILE", help="Read from FILE (default: stdin)")
    p.add_argument("--output", "-o", metavar="FILE", help="Write to FILE (default: stdout)")
    p.add_argument("--verbose", "-v", action="store_true", help="Debug logging to stderr")
    return p


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main(argv: list | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        log.setLevel(logging.DEBUG)

    try:
        raw = read_input(args.input)
        log.debug("Read %d chars", len(raw))

        data, fmt = parse_input(raw)
        log.debug("Format=%s  parsed=%r", fmt, data)

        result = solve(data, fmt)
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