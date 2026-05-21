#!/usr/bin/env python3
import sys
import json
import argparse
import logging
import traceback
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stderr)])
logger = logging.getLogger(__name__)

def build_parser():
    p = argparse.ArgumentParser(description="Competition solution")
    p.add_argument("--input", "-i", metavar="FILE")
    p.add_argument("--output", "-o", metavar="FILE")
    p.add_argument("--verbose", "-v", action="store_true")
    return p

def process(data: str) -> Any:
    data = data.strip()
    if not data:
        raise ValueError("Empty input")
    try:
        parsed = json.loads(data)
        return _process_json(parsed)
    except json.JSONDecodeError:
        return _process_text(data)

def _process_json(payload: Any) -> Any:
    return {"status": "ok", "result": payload}

def _process_text(text: str) -> str:
    return text

def read_input(path: Optional[str]) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()

def write_output(result: Any, path: Optional[str]) -> None:
    text = result if isinstance(result, str) else json.dumps(result, indent=2, ensure_ascii=False)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    try:
        raw = read_input(args.input)
        result = process(raw)
        write_output(result, args.output)
        return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        logger.debug(traceback.format_exc())
        return 3

if __name__ == "__main__":
    sys.exit(main())
