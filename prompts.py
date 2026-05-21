REPAIR_PROMPT_TEMPLATE = """
You are repairing a failing Python program.

Specification summary:
{spec_summary}

Failing test summary:
{failure_summary}

Expected behavior:
{expected_output}

Actual behavior:
{actual_output}

Previous failed repair attempts:
{previous_attempts}

Instructions:
- Re-read the specification carefully.
- Do not repeat previous failed fixes.
- Produce a complete corrected file.
- Preserve working functionality.
- Focus specifically on the failing behavior.
"""