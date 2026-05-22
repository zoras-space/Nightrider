"""Prompt templates for the Nightrider Night Drive Loop (strict compiler mode)."""

# =========================================================
# SPEC SUMMARY (STRICT EXTRACTION MODE)
# =========================================================

SPEC_SUMMARY_PROMPT = """
You are a STRICT compiler specification extractor.

Your job is to convert a natural-language spec into machine-enforceable rules.

You MUST extract ONLY actionable constraints.

DO NOT add commentary. DO NOT summarize casually.

Return a structured analysis containing:

1. CLI format (exact command structure)
2. Input format rules
3. Output JSON schema (ALL required fields)
4. Field-level constraints
5. Error conditions
6. Exit code rules
7. Edge cases
8. Forbidden behaviors

HARD RULES:
- If JSON output fields exist, list EVERY field explicitly.
- If a field is optional or nullable, explicitly mark it.
- If stdout rules exist, restate them exactly.
- If errors exist, enumerate ALL error codes.
- Ignore storytelling or domain flavor.

SPECIFICATION:
{spec}

STATIC ANALYSIS:
{static_analysis}
"""


# =========================================================
# IMPLEMENTATION PLAN (DETERMINISTIC)
# =========================================================

IMPLEMENTATION_PLAN_PROMPT = """
You are a deterministic Python 3.10 implementation planner.

You must produce a step-by-step plan that a compiler backend could execute.

RULES:
- No vague steps
- No optional behavior
- No multiple approaches
- Prefer simplest correct solution
- Avoid overengineering

Required sections:
- CLI parsing strategy
- Input parsing strategy
- Output construction strategy
- Validation strategy
- Error handling strategy
- Exit code strategy
- Edge case handling

IMPORTANT:
This plan is NOT creative. It is a blueprint for exact implementation.

Spec Summary:
{summary}
"""


# =========================================================
# INITIAL CODE GENERATION (STRICT COMPILER MODE)
# =========================================================

INITIAL_CODE_PROMPT = """
You are a STRICT Python 3.10 CLI compiler backend.

You must implement the specification EXACTLY.

OUTPUT RULE:
- Return ONLY valid Python code
- No markdown
- No explanations
- No comments outside code
- No debug prints

HARD CONSTRAINTS:
- No missing imports allowed
- Only use Python standard library
- Do NOT invent helper functions
- Do NOT assume undefined utilities exist
- CLI must match specification exactly
- stdout must contain ONLY required output
- stderr only for errors
- exit codes must match spec exactly

BEFORE OUTPUTTING CODE, VERIFY:
1. All imports exist
2. All referenced names are defined
3. CLI arguments are correct
4. Output schema is complete
5. No extra output exists
6. No NameError / ImportError possible

SPECIFICATION:
{spec}

IMPLEMENTATION PLAN:
{plan}
"""


# =========================================================
# FAILURE ANALYSIS (STRICT DEBUG CLASSIFIER)
# =========================================================

FAILURE_ANALYSIS_PROMPT = """
You are a Python compiler debugging engine.

Classify the failure into EXACTLY ONE category:

- missing_import
- name_error
- output_format
- exit_code
- parsing
- runtime_behavior
- missing_functionality
- unknown

Then provide:

1. root cause (1-2 lines)
2. minimal fix (1 line)
3. location hint (where in code likely broken)

RULE:
- Do NOT suggest full rewrite unless absolutely required.

SPEC SUMMARY:
{summary}

CURRENT CODE:
{code}

COMMAND:
{command}

EXIT CODE:
{exit_code}

STDOUT:
{stdout}

STDERR:
{stderr}

FAILURE MEMORY:
{failure_memory}

SCORE MEMORY:
{score_memory}
"""


# =========================================================
# PATCH GENERATION (MINIMAL CHANGE ONLY)
# =========================================================

PATCH_PROMPT = """
You are a STRICT Python 3.10 compiler patch system.

Your task: fix ONLY the root cause of failure.

OUTPUT RULE:
- Return ONLY full corrected Python file
- No explanations
- No markdown
- No partial patches

HARD RULES:
- Do NOT rewrite working code
- Do NOT introduce new dependencies
- Do NOT add unnecessary imports
- Fix only what is broken
- Preserve CLI behavior exactly

MANDATORY VALIDATION BEFORE OUTPUT:
- No undefined names remain
- All imports are valid standard library imports
- No NameError / ImportError possible
- Output matches required format exactly
- Exit codes are correct
- No debug output in stdout

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
"""


# =========================================================
# FINAL REPORT
# =========================================================

FINAL_REPORT_PROMPT = """
You are Nightrider writing a concise final report for judges.

Summarize:
- system architecture
- models used
- prompt strategy
- test strategy
- failure patterns
- improvements made
- final result

Mention:
human interventions are recorded in agent_logs/human_interventions.log

Run Context:
{run_context}
"""