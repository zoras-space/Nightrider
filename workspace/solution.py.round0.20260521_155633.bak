from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: solution.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"could not read file: {exc}", file=sys.stderr)
        return 1

    result = {
        "line_count": len(text.splitlines()),
        "word_count": len(text.split()),
        "char_count": len(text),
    }
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
