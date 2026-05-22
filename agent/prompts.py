"""Prompt templates for Nightrider agent (schema-first version)."""

SPEC_SUMMARY_PROMPT = """You are a strict spec extraction engine for a CLI compiler task.

Your job is NOT to explain the spec.
Your job is to extract a machine-usable contract.

You MUST output:

1. REQUIRED CLI COMMAND
2. REQUIRED OUTPUT JSON SCHEMA (STRICT)
3. REQUIRED FIELDS (list all JSON keys)
4. VALIDATION RULES
5. ERROR CONDITIONS
6. EDGE CASES
7. FORBIDDEN OUTPUT BEHAVIOR (very important)

Be precise. Do NOT hallucinate extra fields.

SPEC:
{spec}

STATIC ANALYSIS:
{static_analysis}
"""

IMPLEMENTATION_PLAN_PROMPT = """You are a senior compiler engineer building a CLI program.

You MUST follow this rule:

👉 The output JSON schema is a HARD CONTRACT. Never deviate.

Before writing code, explicitly define:

1. FINAL JSON SCHEMA (must match spec exactly)
2. REQUIRED OUTPUT KEYS (mandatory)
3. OPTIONAL KEYS (if any)
4. DEFAULT VALUES
5. ERROR HANDLING STRATEGY
6. PARSING STRATEGY
7. EXECUTION FLOW

Then write a deterministic implementation plan.

IMPORTANT RULES:
- stdout = ONLY JSON
- stderr = logs/errors only
- exit codes must match spec
- missing field = immediate failure risk

SPEC SUMMARY:
{summary}
"""

INITIAL_CODE_PROMPT = """You are generating a production-grade CLI solution.

CRITICAL RULES:
- Output EXACTLY ONE JSON object to stdout
- NO debug prints
- NO extra text
- NO logging to stdout
- stderr allowed for errors only
- MUST match schema exactly

Before coding, ensure:
- every required JSON field exists
- field names match spec EXACTLY
- no missing keys like 'nonempty_line_count'
- all imports are valid

SPEC:
{spec}

PLAN:
{plan}

Return ONLY Python code for {program_path}.
"""

FAILURE_ANALYSIS_PROMPT = """You are debugging a failing CLI compiler.

You must identify the EXACT root cause.

Classify into:
- missing_field
- wrong_output_schema
- parsing_error
- runtime_crash
- exit_code_error
- logic_error

IMPORTANT:
If output is missing a field (e.g. nonempty_line_count), ALWAYS classify as:
→ wrong_output_schema

SPEC SUMMARY:
{summary}

CODE:
{code}

COMMAND:
{command}

EXIT CODE:
{exit_code}

STDOUT:
{stdout}

STDERR:
{stderr}

FAILURE HISTORY:
{failure_memory}

SCORES:
{score_memory}
"""

PATCH_PROMPT = """You are fixing a failing CLI program.

RULES:
- Fix ONLY the root cause
- Do NOT rewrite unrelated parts
- Ensure output JSON matches schema EXACTLY
- Missing fields are NOT allowed under any condition

COMMON FAILURE FIXES:
- missing field → add field in JSON output
- wrong key name → rename key exactly
- runtime crash → fix import / variable

SPEC SUMMARY:
{summary}

CURRENT CODE:
{code}

FAILURE ANALYSIS:
{failure_analysis}

LATEST STDOUT:
{stdout}

LATEST STDERR:
{stderr}

Return ONLY full corrected Python code for {program_path}.
"""

FINAL_REPORT_PROMPT = """You are writing a concise final engineering report.

Include:
- success/failure
- failure categories
- schema issues encountered
- repair effectiveness
- remaining risks

RUN CONTEXT:
{run_context}
"""