from dataclasses import dataclass


@dataclass
class TestResult:
    passed: bool
    failure_summary: str = ""
    stdout: str = ""
    stderr: str = ""


class FailureTracker:
    def __init__(self):
        self.previous_failure = None
        self.repeat_count = 0

    def update(self, failure_message: str) -> bool:
        normalized = failure_message.strip().lower()

        if normalized == self.previous_failure:
            self.repeat_count += 1
        else:
            self.repeat_count = 1
            self.previous_failure = normalized

        return self.repeat_count >= 3

    def reset(self):
        self.previous_failure = None
        self.repeat_count = 0


def classify_failure(message: str) -> str:
    text = message.lower()

    if "missing" in text:
        return "missing_output"

    if "traceback" in text:
        return "runtime"

    if "assert" in text:
        return "logic"

    if "timeout" in text:
        return "timeout"

    return "unknown"


def build_repair_prompt(
    spec_summary: str,
    failure_summary: str,
    stdout: str,
    stderr: str,
    escalate: bool,
) -> str:

    prompt = f"""
You are repairing a failing Python CLI program.

SPECIFICATION SUMMARY:
{spec_summary}

FAILING TEST SUMMARY:
{failure_summary}

STDOUT:
{stdout}

STDERR:
{stderr}

Instructions:
- Fix the failing behavior
- Preserve existing working behavior
- Produce a complete corrected file
"""

    if escalate:
        prompt += """

IMPORTANT:
Previous repair attempts failed repeatedly.

You MUST:
- Re-read the entire specification carefully
- Reconstruct all required output fields
- Compare expected vs actual behavior carefully
- Avoid repeating previous failed fixes
- Produce a complete corrected implementation
"""

    return prompt


def run_repair_loop(
    max_rounds,
    spec_summary,
    run_tests,
    generate_solution,
):
    """
    run_tests() -> TestResult
    generate_solution(prompt: str) -> None
    """

    failure_tracker = FailureTracker()

    repairs = []

    for round_number in range(1, max_rounds + 1):

        print("\n" + "─" * 56)
        print(f"[Round {round_number}/{max_rounds}] Run tests")

        result = run_tests()

        if result.passed:
            print("✅ Passed")

            failure_tracker.reset()

            print("\nFinal status: passed")

            return True

        print("❌ Failed")

        failure_type = classify_failure(result.failure_summary)

        print("\nFailure type:")
        print(f"- {failure_type}")

        print("\nWhat failed:")
        print(f"- {result.failure_summary}")

        escalate = failure_tracker.update(result.failure_summary)

        if escalate:
            print("\nRepeated identical failure detected.")
            print("Escalating repair strategy.")

        repair_prompt = build_repair_prompt(
            spec_summary=spec_summary,
            failure_summary=result.failure_summary,
            stdout=result.stdout,
            stderr=result.stderr,
            escalate=escalate,
        )

        print("\nFixing:")
        print("Generating targeted repair...")

        generate_solution(repair_prompt)

        repairs.append(
            {
                "round": round_number,
                "failure": result.failure_summary,
                "failure_type": failure_type,
                "escalated": escalate,
            }
        )

    print("\n" + "─" * 56)
    print("❌ Final status: not passed")
    print(f"Rounds used: {max_rounds}/{max_rounds}")

    print("\nRepairs attempted:")

    for repair in repairs:
        escalation_text = (
            " (escalated)"
            if repair["escalated"]
            else ""
        )

        print(
            f"- Round {repair['round']}: "
            f"{repair['failure_type']}"
            f"{escalation_text}"
        )

    return False