#!/usr/bin/env python3
"""
agent.py — Autonomous implementation-and-repair loop
=====================================================

Usage (after hidden spec is released):
    python3 agent.py --spec secret_spec/SPEC.md --max-iterations 30

What it does:
  1. Reads the spec
  2. Asks Qwen to make a plan
  3. Asks Qwen to implement solve()
  4. Runs public tests
  5. If failures: asks Qwen to patch, Llama to review
  6. Repeats until 100% or max iterations
  7. Logs everything to agent_logs/
"""

import subprocess
import sys
import json
import re
import argparse
import logging
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
CODER_MODEL = "qwen2.5-coder:7b"
REVIEWER_MODEL = "llama3.1:8b"
SOLUTION_FILE = Path("solution.py")
LOGS_DIR = Path("agent_logs")
TEST_RUNNER = "python3 secret_spec/test_runner/run_tests.py"
TEST_PROGRAM = "python3 solution.py"
MAX_SAME_SCORE = 3  # escalate if score doesn't improve after this many tries

logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# LOGGING HELPERS
# ──────────────────────────────────────────────
def ts() -> str:
    return datetime.now().strftime("[%Y-%m-%d %H:%M]")


def append_log(filename: str, label: str, content: str) -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    path = LOGS_DIR / filename
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n{ts()} {label}:\n{content.strip()}\n")


def log_prompt(content):     append_log("prompts.log", "USER_PROMPT", content)


def log_decision(content):   append_log("decisions.log", "DECISION", content)


def log_command(content):    append_log("commands.log", "COMMAND", content)


def log_test_run(content):   append_log("test_runs.log", "TEST_RUN", content)


def log_error(content):      append_log("errors.log", "ERROR", content)


def log_intervention(content): append_log("human_interventions.log", "HUMAN_INTERVENTION", content)


# ──────────────────────────────────────────────
# SHELL HELPERS
# ──────────────────────────────────────────────
def run_cmd(cmd: str, timeout: int = 60) -> tuple[int, str, str]:
    """Run a shell command, return (exit_code, stdout, stderr)."""
    log_command(cmd)
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )
    return result.returncode, result.stdout, result.stderr


def git_commit(message: str) -> None:
    run_cmd(f'git add -A && git commit -m "{message}" --allow-empty')


# ──────────────────────────────────────────────
# OLLAMA HELPERS
# ──────────────────────────────────────────────
def ollama(model: str, prompt: str, timeout: int = 120) -> str:
    """Call an Ollama model and return its text output."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False})
    code, out, err = run_cmd(
        f"curl -s http://localhost:11434/api/generate -d '{payload}'",
        timeout=timeout,
    )
    if code != 0:
        log_error(f"Ollama call failed: {err}")
        return ""
    try:
        return json.loads(out).get("response", "")
    except json.JSONDecodeError:
        log_error(f"Ollama bad JSON response: {out[:200]}")
        return ""


def ask_coder(prompt: str) -> str:
    log_prompt(prompt[:500] + ("..." if len(prompt) > 500 else ""))
    return ollama(CODER_MODEL, prompt)


def ask_reviewer(prompt: str) -> str:
    return ollama(REVIEWER_MODEL, prompt)


# ──────────────────────────────────────────────
# TEST RUNNER PARSER
# ──────────────────────────────────────────────
def run_tests() -> dict:
    """
    Run the public test suite and return:
      { score: int, total: int, pct: float, failures: [{ name, expected, actual }] }
    """
    cmd = f"{TEST_RUNNER} --program '{TEST_PROGRAM}' --suite public --verbose"
    code, out, err = run_cmd(cmd, timeout=120)
    log_test_run(out)

    # Parse score line:  "Score: 70/80  (7/8 tests passed)"
    score, total = 0, 80
    m = re.search(r"Score:\s*(\d+)/(\d+)", out)
    if m:
        score, total = int(m.group(1)), int(m.group(2))

    # Parse failures
    failures = []
    for block in re.finditer(r"✗ FAIL\s+(\S+).*?(?=✓|✗|Score:|$)", out, re.DOTALL):
        name = block.group(1)
        exp = re.search(r"Expected(?:\s+stdout)?:\s*(.+?)(?=Actual|Error|$)", block.group(0), re.DOTALL)
        act = re.search(r"Actual(?:\s+stdout)?:\s*(.+?)(?=Expected|Error|$)", block.group(0), re.DOTALL)
        failures.append({
            "name": name,
            "expected": exp.group(1).strip() if exp else "?",
            "actual": act.group(1).strip() if act else "?",
        })

    pct = round(score / total * 100) if total else 0
    return {"score": score, "total": total, "pct": pct, "failures": failures}


# ──────────────────────────────────────────────
# EXTRACT / APPLY CODE
# ──────────────────────────────────────────────
def extract_python(response: str) -> str:
    """Pull Python out of model response (strips markdown fences if present)."""
    # Try fenced block first
    m = re.search(r"```python\s*(.*?)```", response, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*(.*?)```", response, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Assume the whole response is code if it starts with import/def/#!
    if re.match(r"(#!/|import |from |def |#)", response.strip()):
        return response.strip()
    return ""


def apply_code(code: str) -> bool:
    """Write code to solution.py. Returns True if successful."""
    if not code or len(code) < 50:
        log_error("Generated code too short, refusing to apply.")
        return False
    # Basic sanity: must define main() and solve()
    if "def solve(" not in code or "def main(" not in code:
        log_error("Generated code missing solve() or main(), refusing to apply.")
        return False
    SOLUTION_FILE.write_text(code, encoding="utf-8")
    return True


# ──────────────────────────────────────────────
# PROMPT BUILDERS
# ──────────────────────────────────────────────
def prompt_plan(spec: str) -> str:
    return f"""You are a competition programmer.
Read this specification and create a numbered implementation plan.
Do NOT write any code yet. Just plan.

SPECIFICATION:
{spec}

Output a numbered list of implementation steps only."""


def prompt_implement(spec: str, current_code: str) -> str:
    return f"""You are a competition programmer. Output ONLY valid Python 3. No explanation.
No markdown fences. No extra text before or after the code.

SPECIFICATION:
{spec}

CURRENT solution.py (infrastructure — do not change read_input, parse_input signature, 
write_output, format_output, build_parser, main):
{current_code}

TASK: Rewrite the solve(), _solve_json(), _solve_csv(), _solve_lines(), _solve_text()
functions to correctly implement the specification. Keep all other functions unchanged.
Output the complete corrected solution.py file."""


def prompt_patch(spec_summary: str, current_code: str, failures: list) -> str:
    failure_text = "\n".join(
        f"  FAIL: {f['name']}\n    expected: {f['expected']}\n    got:      {f['actual']}"
        for f in failures
    )
    return f"""You are a competition programmer. Output ONLY valid Python 3. No explanation.
No markdown fences. No extra text.

SPEC RULES (relevant excerpt):
{spec_summary}

FAILING TESTS:
{failure_text}

CURRENT solution.py:
{current_code}

TASK: Fix the failing tests. Output the complete corrected solution.py."""


def prompt_review(patch_diff: str, failures: list) -> str:
    failure_text = "\n".join(f"  {f['name']}: expected {f['expected'][:80]}" for f in failures)
    return f"""You are a code reviewer. Answer in one word: GOOD or BAD.
Then one sentence explaining why.

FAILING TESTS that this patch tries to fix:
{failure_text}

PATCH (git diff):
{patch_diff}

Does this patch correctly address the failures without introducing regressions?
Answer: GOOD or BAD, then one sentence."""


def prompt_escalate(spec: str, current_code: str, failures: list, iteration: int) -> str:
    failure_text = "\n".join(f"  {f['name']}" for f in failures)
    return f"""You are a competition programmer. The same tests have been failing for
{iteration} iterations. Try a completely different approach.

STILL FAILING:
{failure_text}

SPECIFICATION:
{spec}

Output ONLY the complete corrected solution.py. Different logic from before."""


# ──────────────────────────────────────────────
# MAIN AGENT LOOP
# ──────────────────────────────────────────────
def run_agent(spec_path: str, max_iterations: int = 30) -> None:
    spec = Path(spec_path).read_text(encoding="utf-8")
    log.info("Spec loaded: %d chars", len(spec))

    # ── Phase 1: Plan ──────────────────────────
    log.info("Planning...")
    plan = ask_coder(prompt_plan(spec))
    log_decision(f"Implementation plan:\n{plan}")
    log.info("Plan complete.")

    # ── Phase 2: Initial implementation ────────
    log.info("Generating initial implementation...")
    current_code = SOLUTION_FILE.read_text(encoding="utf-8")
    response = ask_coder(prompt_implement(spec, current_code))
    new_code = extract_python(response)

    if apply_code(new_code):
        git_commit("agent: initial implementation")
        log.info("Initial implementation applied.")
    else:
        log_error("Initial implementation failed extraction, continuing with stub.")

    # ── Phase 3: Test → Patch loop ─────────────
    last_score = -1
    same_score_count = 0

    for iteration in range(1, max_iterations + 1):
        log.info("── Iteration %d/%d ──", iteration, max_iterations)

        result = run_tests()
        score_line = f"Score: {result['score']}/{result['total']} ({result['pct']}%)"
        log.info(score_line)

        if result["pct"] == 100:
            log.info("✓ 100%% — done!")
            log_decision(f"Reached 100%% at iteration {iteration}.")
            break

        # Stuck detection
        if result["score"] == last_score:
            same_score_count += 1
        else:
            same_score_count = 0
        last_score = result["score"]

        failures = result["failures"]
        current_code = SOLUTION_FILE.read_text(encoding="utf-8")

        # Escalate if stuck
        if same_score_count >= MAX_SAME_SCORE:
            log.warning("Score stuck at %d for %d iterations — escalating.", result["score"], same_score_count)
            log_decision(f"Escalating after {same_score_count} iterations without improvement.")
            response = ask_coder(prompt_escalate(spec, current_code, failures, same_score_count))
            same_score_count = 0
        else:
            # Normal patch
            spec_summary = spec[:2000]  # keep context tight for 7b model
            response = ask_coder(prompt_patch(spec_summary, current_code, failures))

        new_code = extract_python(response)
        if not new_code:
            log_error(f"Iteration {iteration}: empty code extraction, skipping.")
            continue

        # ── Reviewer check ──────────────────────
        _, diff_out, _ = run_cmd("git diff solution.py")
        if diff_out:
            review = ask_reviewer(prompt_review(diff_out, failures))
            log_decision(f"Reviewer verdict (iteration {iteration}): {review[:200]}")
            if "BAD" in review.upper() and "GOOD" not in review.upper():
                log.warning("Reviewer said BAD — applying anyway but noting it.")

        # ── Apply ───────────────────────────────
        if apply_code(new_code):
            git_commit(f"agent: iteration {iteration} — {score_line}")
            log.info("Patch applied and committed.")
        else:
            log_error(f"Iteration {iteration}: bad code, not applied.")

    else:
        log.warning("Max iterations reached without 100%%.")
        log_decision(f"Stopped after {max_iterations} iterations. Final score: {last_score}.")

    # ── Final report ────────────────────────────
    final_result = run_tests()
    report = f"""## Final Score
{final_result['score']}/{final_result['total']} ({final_result['pct']}%)

## Remaining Failures
{json.dumps(final_result['failures'], indent=2) if final_result['failures'] else 'None'}

## Iterations Used
{iteration}
"""
    (LOGS_DIR / "final_report.md").write_text(report, encoding="utf-8")
    log.info("Final report written.")
    git_commit("agent: final submission")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Autonomous competition agent")
    p.add_argument("--spec", default="secret_spec/SPEC.md", help="Path to spec file")
    p.add_argument("--max-iterations", type=int, default=30)
    args = p.parse_args()

    if not Path(args.spec).exists():
        print(f"ERROR: spec not found at {args.spec}", file=sys.stderr)
        print("Wait for the hidden spec release, then run:", file=sys.stderr)
        print(f"  python3 agent.py --spec {args.spec}", file=sys.stderr)
        sys.exit(1)

    run_agent(args.spec, args.max_iterations)


if __name__ == "__main__":
    main()