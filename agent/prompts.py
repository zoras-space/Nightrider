"""


EXPECTED_OUTPUT_BATCH_PROMPT = """You are generating official-style expected-output JSON for multiple Knitting Compiler tests.

For each test, produce exactly one JSON object matching the expected-output wrapper schema.
Return a JSON object whose keys are test IDs and whose values are expected-output wrapper objects.
Do not include Markdown.
Do not explain.

{schema_prompt}

Specification or relevant excerpt:
{spec}

Official expected-output examples:
{examples}

Tests:
{tests}

Return JSON only.
"""


# Compatibility names used by the existing Nightrider agent loop.
# They now steer the model toward expected-output generation instead of code repair.

SPEC_SUMMARY_PROMPT = """You are Nightrider preparing to generate expected-output JSON files.

Extract the output contract from the specification:
- wrapper schema
- stdout schema for valid cases
- stdout schema for invalid cases
- exit code rules
- expanded row schema
- error object schema
- line and row numbering rules
- normalization rules
- ordering rules

Specification:
{spec}
"""

IMPLEMENTATION_PLAN_PROMPT = """Create a concise plan for generating expected-output JSON from test metadata and .knit input files.

The plan must include:
- how to read metadata
- how to parse the .knit input
- how to compute valid stdout
- how to collect errors
- how to match official examples
- how to self-check and repair JSON output

Spec summary:
{summary}
"""

INITIAL_CODE_PROMPT = """You are not writing compiler code.

Generate an expected-output JSON document in the official format.
Return JSON only.
Do not include Python.
Do not include Markdown.

Specification:
{spec}

Plan:
{plan}
"""

FAILURE_ANALYSIS_PROMPT = """Analyze why the generated expected-output JSON failed validation.

Classify the failure as one of:
- invalid JSON
- wrong wrapper schema
- wrong stdout schema
- wrong exit code
- wrong expanded rows
- wrong error list
- wrong line or row number
- wrong field order or extra field
- unknown

Be concise.

Spec summary:
{summary}

Current output:
{code}

Validation command:
{command}

Exit code: {exit_code}

Stdout:
{stdout}

Stderr:
{stderr}

Previous failure memory:
{failure_memory}

Visible score memory:
{score_memory}
"""

PATCH_PROMPT = """Repair the generated expected-output JSON.

Return JSON only.
Do not include Markdown.
Do not explain.
Patch only what the feedback requires.

Spec summary:
{summary}

Current output:
{code}

Failure analysis:
{failure_analysis}

Latest validation stdout:
{stdout}

Latest validation stderr:
{stderr}
"""

FINAL_REPORT_PROMPT = """Write a concise Markdown report for the expected-output generation run.

Include:
- model used
- inputs used
- examples used
- validation strategy
- failures corrected
- remaining risks

Run context:
{run_context}
"""