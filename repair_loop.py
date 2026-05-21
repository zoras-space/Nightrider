from collections import Counter


class FailureTracker:
    def __init__(self):
        self.failures = []

    def add(self, failure_message: str):
        self.failures.append(failure_message)

    def repeated_count(self, failure_message: str) -> int:
        return Counter(self.failures)[failure_message]


failure_tracker = FailureTracker()


def should_escalate(failure_message: str) -> bool:
    failure_tracker.add(failure_message)
    return failure_tracker.repeated_count(failure_message) >= 3


# Example integration inside your repair loop:

# if should_escalate(summary):
#     print("Repeated identical failure detected.")
#     print("Escalating repair strategy.")
#     repair_prompt += "\n\nIMPORTANT: Previous fixes fail