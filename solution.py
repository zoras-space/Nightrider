#!/usr/bin/env python3
"""
Competition solution entry point.

Usage:
    python3 solution.py [--input <file>] [--output <file>] [--verbose]
    echo '...' | python3 solution.py

The hidden specification will define the exact input/output contract.
This scaffold handles CLI, I/O routing, structured error output, and logging hooks.
"""

import sys
import json
import argparse
import logging
import traceback
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Competition solution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="Input file (default: stdin)",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file (default: stdout)",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging to stderr",
    )
    return p


# ---------------------------------------------------------------------------
# Core processing — REPLACE this with spec-driven logic
# ---------------------------------------------------------------------------
def process(data: str) -> Any:
    """
    Transform raw input text into output.

    Replace the body of this function once the hidden spec is known.
    Contract:
        - Input:  raw string read from stdin or --input file
        - Output: any JSON-serialisable value, or a plain string

    Current stub: echoes back parsed JSON, or wraps plain text in an object.
    """
    data = data.strip()
    if not data:
        raise ValueError("Empty input")

    # Attempt JSON parse first — many competition tasks use JSON I/O
    try:
        parsed = json.loads(data)
        return _process_json(parsed)
    except json.JSONDecodeError:
        return _process_text(data)


def _process_json(payload: Any) -> Any:
    """Handle JSON-structured input. Stub — replace with real logic."""
    # Example transform: return as-is with a status wrapper
    return {"status": "ok", "result": payload}


def _process_text(text: str) -> str:
    """Handle plain-text input. Stub — replace with real logic."""
    return text


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------
def read_input(path: Optional[str]) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def write_output(result: Any, path: Optional[str]) -> None:
    if isinstance(result, str):
        text = result
    else:
        text = json.dumps(result, indent=2, ensure_ascii=False)

    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        raw = read_input(args.input)
        logger.debug("Read %d bytes of input", len(raw))

        result = process(raw)
        logger.debug("Processing complete")

        write_output(result, args.output)
        return 0

    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        logger.debug(traceback.format_exc())
        return 1

    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    except Exception as exc:  # noqa: BLE001
        print(f"FATAL: Unexpected error — {exc}", file=sys.stderr)
        logger.debug(traceback.format_exc())
        return 3


if __name__ == "__main__":
    sys.exit(main())
