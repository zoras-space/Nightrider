"""Safe full-file editing utilities for generated solution files."""

from __future__ import annotations

import re
import shutil
import difflib
import py_compile
import tempfile
from datetime import datetime
from pathlib import Path


CODE_FENCE_PATTERN = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def inspect_file(path: Path, max_chars: int = 8000) -> str:
    """Return a bounded view of a file for prompts and logs."""

    if not path.exists():
        return "<missing>"
    content = read_file(path)
    if len(content) <= max_chars:
        return content
    return content[-max_chars:]


def extract_code(text: str) -> str:
    """Return Python from a Markdown fence when present, otherwise raw text."""

    matches = CODE_FENCE_PATTERN.findall(text)
    if matches:
        return matches[0].strip() + "\n"
    return text.strip() + "\n"


def backup_file(path: Path, round_number: int | None = None) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    round_label = f".round{round_number}" if round_number is not None else ""
    backup_path = path.with_name(f"{path.name}{round_label}.{stamp}.bak")
    shutil.copy2(path, backup_path)
    return backup_path


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate_python_source(content: str, path: Path) -> tuple[bool, str]:
    """Compile source in a temporary file before accepting it."""

    if path.suffix != ".py":
        return True, "non-Python file"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
        temp_path = Path(handle.name)
        handle.write(content)
    try:
        py_compile.compile(str(temp_path), doraise=True)
    except py_compile.PyCompileError as exc:
        return False, str(exc)
    finally:
        temp_path.unlink(missing_ok=True)
    return True, "ok"


def replace_file_from_model(path: Path, model_text: str, round_number: int | None = None) -> Path | None:
    """Back up the old file and replace it with model-returned code."""

    code = extract_code(model_text)
    valid, message = validate_python_source(code, path)
    if not valid:
        raise ValueError(f"Rejected invalid Python for {path}: {message}")
    backup_path = backup_file(path, round_number=round_number)
    write_file(path, code)
    return backup_path


def summarize_change(before: str, after: str, path: Path, max_lines: int = 80) -> str:
    """Create a concise unified diff summary for logging."""

    if before == after:
        return f"No textual changes detected in {path}."
    diff_lines = list(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=f"{path} before",
            tofile=f"{path} after",
            lineterm="",
        )
    )
    clipped = diff_lines[:max_lines]
    suffix = "\n... diff clipped ..." if len(diff_lines) > max_lines else ""
    return "\n".join(clipped) + suffix


def replace_file_from_model_with_summary(
    path: Path,
    model_text: str,
    round_number: int | None = None,
) -> tuple[Path | None, str]:
    """Back up, replace, and return a short change summary."""

    before = read_file(path) if path.exists() else ""
    backup_path = replace_file_from_model(path, model_text, round_number=round_number)
    after = read_file(path)
    return backup_path, summarize_change(before, after, path)
