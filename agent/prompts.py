"""Prompt templates for the Knitting Pattern DSL Compiler."""

SSPEC_SUMMARY_PROMPT = """You are Nightrider. The tool reads a file and prints JSON statistics to stdout.

The problem changes depending on the file extension or content pattern:
- .txt files: Count lines, words, characters → output {"line_count": int, "word_count": int, "char_count": int}
- commands.txt: Process ADD/REMOVE/TOTAL commands → output {"inventory": {...}, "totals": [...]}
- .json files: Transform objects (strip names, add active=False default) → output array of transformed objects

CRITICAL:
The visible task description may be incomplete.
Hidden tests may require additional fields, edge cases, validation rules,
or exact CLI/output behavior not obvious from the short summary.

You MUST aggressively infer:
- hidden required JSON fields (NEVER add extra fields like nonempty_line_count)
- strict schema matching (exactly the fields shown in examples)
- exact exit code behavior (0 on success, 1 on argument/file errors)
- malformed input handling (syntax errors → exit 1)
- stdout/stderr separation (JSON only on stdout, errors on stderr)
- ordering requirements (preserve input order for inventory items)
- duplicate handling (inventory commands)
- edge cases (empty files, missing fields, invalid quantities)
- validation logic (REMOVE too many → error, malformed command → error)

Return a structured summary with these exact headings:

- Required command
- Arguments
- Input format
- Output format
- Required JSON fields
- Exit codes
- Error behavior
- Validation rules
- Edge cases
- Hidden test risks
- Likely failure points

Specification:
{spec}
"""

IMPLEMENTATION_PLAN_PROMPT = """You are Nightrider planning a Python CLI implementation.

You are building against hidden tests.

The visible examples are NOT sufficient.

You MUST design for:
- strict parser correctness
- exact JSON schema matching
- hidden required fields
- deterministic ordering
- malformed input recovery
- exit code correctness
- stderr/stdout separation
- edge-case handling
- duplicate detection
- robust validation

Do not simplify the spec.

Keep stdout completely clean.
Only required machine-readable output belongs on stdout.

Use stderr for diagnostics.

Prefer standard library only.

Return a concise but rigorous implementation plan with these headings:

- Parser architecture
- Validation pipeline
- Internal data structures
- JSON schema strategy
- Error handling strategy
- Simulation strategy
- Repeat expansion strategy
- Output strategy
- Exit code strategy
- Hidden test defense strategy
- Test strategy
- Risks to watch

Spec summary:
{summary}
"""


INITIAL_CODE_PROMPT = """You are Nightrider writing the initial solution file for a CLI programming challenge.

Return ONLY the complete Python source for {program_path}.

No explanations.
No markdown outside a single optional python code block.

CRITICAL REQUIREMENTS:

- Hidden tests are strict.
- Exact JSON schema matters.
- Missing required fields will fail.
- Extra stdout text will fail.
- Exit codes matter.
- Ordering matters.
- Edge cases matter.
- Deterministic output matters.

Before writing code:
1. Re-check every required JSON field.
2. Re-check every exit code rule.
3. Re-check malformed input behavior.
4. Re-check parser edge cases.
5. Re-check hidden inferred requirements.

Implementation requirements:
- Python 3.10+
- Standard library preferred
- Robust parsing
- Deterministic output
- No debug prints
- No logging to stdout
- stderr only for diagnostics
- Defensive validation
- Full schema compliance

Specification:
{spec}

Implementation plan:
{plan}
"""


FAILURE_ANALYSIS_PROMPT = """You are Nightrider analyzing a failed hidden test run.

You are repairing against hidden tests.

DO NOT trust the visible summary alone.

Your job:
- infer what hidden requirement is missing
- identify exact schema mismatches
- detect missing fields
- detect parser edge cases
- detect exit code mistakes
- detect ordering issues
- detect hidden validation requirements

Classify the failure as one of:
- parsing
- output format
- exit code
- runtime behavior
- missing functionality
- validation
- ordering
- hidden schema mismatch
- unknown

IMPORTANT:
If the SAME failure repeats,
assume the previous repair did NOT address root cause.

Repeated identical failures usually mean:
- the wrong file was edited
- hidden schema was ignored
- model anchored on visible spec only
- parser architecture is fundamentally wrong
- required field exists in hidden tests but not visible examples

When repeated failures occur:
- propose a deeper repair
- reconsider assumptions
- suggest architectural changes if needed

Be concise but precise.

Specification summary:
{summary}

Current code:
{code}

Test command:
{command}

Exit code:
{exit_code}

Stdout:
{stdout}

Stderr:
{stderr}

Previous failure memory:
{failure_memory}

Visible score memory:
{score_memory}
"""


PATCH_PROMPT = """You are Nightrider repairing a Python CLI solution.

Return ONLY the complete corrected Python source for {program_path}.

Full-file replacement is expected.

CRITICAL:
You are repairing against hidden tests.

DO NOT make superficial patches.

Before patching:
- identify the actual hidden requirement
- verify whether the current architecture supports it
- confirm required JSON fields
- confirm exit code behavior
- confirm parser correctness
- confirm deterministic ordering

Patch rules:
- fix root causes
- avoid regressions
- preserve passing behavior
- keep stdout clean
- stderr only for diagnostics
- standard library preferred

If the same failure repeated multiple times:
- assume previous repair strategy failed
- make a deeper correction
- reconsider assumptions from visible examples

Common hidden-test failures for knitting pattern compiler:
- missing JSON fields (bind_off, cast_on, errors, expanded_rows, final_stitch_count, pattern_name, valid)
- wrong null handling (errors empty list vs null)
- wrong ordering (expanded_rows order)
- malformed input handling (syntax errors)
- duplicate pattern_name validation
- hidden validation logic (empty rows, zero repeats)
- wrong exit codes (parse error = 1, validation error = 0 with valid=false)
- extra stdout text (debug prints)
- parser ambiguity (repeat nesting)
- incomplete schema (stitch types)

Specification summary:
{summary}

Current code:
{code}

Failure analysis:
{failure_analysis}

Latest test stdout:
{stdout}

Latest test stderr:
{stderr}
"""


FINAL_REPORT_PROMPT = """You are Nightrider writing a concise final report for hackathon judges.

Summarize:
- architecture
- models used
- tools available
- prompting strategy
- repair loop strategy
- hidden test strategy
- parser strategy
- validation strategy
- score progression
- failures encountered
- repeated failure handling
- human interventions
- lessons learned
- remaining risks

Mention:
human interventions are logged in
agent_logs/human_interventions.log

Use Markdown.

Run context:
{run_context}
"""