"""Small deterministic repair guardrails for common generated Python mistakes."""

from __future__ import annotations

import re
from pathlib import Path

from agent import file_editor, logger


def apply_python_sanity_repairs(path: Path, round_number: int) -> bool:
    """Apply narrow, explainable repairs before asking the model again."""

    if not path.exists() or path.suffix != ".py":
        return False

    before = file_editor.read_file(path)
    after = before
    notes: list[str] = []

    if "sys." in after and not re.search(r"^import sys$|^from sys import ", after, flags=re.MULTILINE):
        after = _insert_import(after, "import sys")
        notes.append("Added missing import sys because generated code references sys.")

    argparse_destinations = re.findall(r"parser\.add_argument\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]", after)
    for dest in argparse_destinations:
        len_check_pattern = re.compile(
            rf"\n(?P<indent>[ \t]+)if len\(args\.{re.escape(dest)}\) != 1:\n"
            rf"(?P=indent)[ \t]+print\([^\n]*\n"
            rf"(?P=indent)[ \t]+sys\.exit\([^\n]*\n",
            flags=re.MULTILINE,
        )
        after, count = len_check_pattern.subn("\n", after)
        if count:
            notes.append(
                f"Removed invalid len(args.{dest}) check; argparse positional values are strings unless nargs is used."
            )

        indexed = f"args.{dest}[0]"
        if indexed in after:
            after = after.replace(indexed, f"args.{dest}")
            notes.append(f"Replaced {indexed} with args.{dest}.")

    if "content = file.read()" in after and "char_count = sum(len(line) for line in lines)" in after:
        after = after.replace("char_count = sum(len(line) for line in lines)", "char_count = len(content)")
        notes.append("Changed char_count to len(content) so newline characters are counted.")

    if after == before:
        return False

    backup, change_summary = file_editor.replace_file_from_model_with_summary(
        path,
        after,
        round_number=round_number,
    )
    logger.log_decision(
        "Applied deterministic Python sanity repair before model patching.\n"
        f"Backup: {backup or '<none>'}\n"
        f"Notes:\n- " + "\n- ".join(notes) + f"\nChange summary:\n{change_summary}"
    )
    return True


def _insert_import(code: str, import_line: str) -> str:
    lines = code.splitlines()
    insert_at = 0
    for index, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = index + 1
    lines.insert(insert_at, import_line)
    return "\n".join(lines) + "\n"

