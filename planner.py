import re
from dataclasses import dataclass
from typing import List


IMPORTANT_REQUIREMENT_KEYWORDS = [
    "must",
    "required",
    "include",
    "json",
    "field",
    "output",
    "edge case",
    "error",
    "stderr",
    "stdout",
    "exit code",
    "return",
    "print",
    "cli",
]


@dataclass
class PlanResult:
    purpose: str
    requirements: List[str]
    output_fields: List[str]
    edge_cases: List[str]
    implementation_plan: List[str]
    summary: str


def normalize_line(line: str) -> str:
    return " ".join(line.strip().split())


def extract_purpose(spec_text: str) -> str:
    lines = [line.strip() for line in spec_text.splitlines() if line.strip()]

    for line in lines:
        lowered = line.lower()

        if lowered.startswith("purpose:"):
            return line

    if lines:
        return lines[0]

    return "No purpose detected."


def extract_requirements(spec_text: str) -> List[str]:
    requirements = []

    for line in spec_text.splitlines():
        cleaned = normalize_line(line)

        if not cleaned:
            continue

        lowered = cleaned.lower()

        if any(keyword in lowered for keyword in IMPORTANT_REQUIREMENT_KEYWORDS):
            requirements.append(cleaned)

    return sorted(set(requirements))


def extract_output_fields(spec_text: str) -> List[str]:
    fields = set()

    patterns = [
        r'"([a-zA-Z0-9_]+)"',
        r"'([a-zA-Z0-9_]+)'",
        r"\b([a-zA-Z_]+_count)\b",
        r"\b(id|name|active|status|result|error)\b",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, spec_text)

        for match in matches:
            if isinstance(match, tuple):
                for item in match:
                    if item:
                        fields.add(item)
            else:
                fields.add(match)

    return sorted(fields)


def extract_edge_cases(spec_text: str) -> List[str]:
    edge_cases = []

    EDGE_CASE_KEYWORDS = [
        "empty",
        "missing",
        "invalid",
        "error",
        "stderr",
        "nonzero",
        "not found",
        "must fail",
        "incorrect",
    ]

    for line in spec_text.splitlines():
        cleaned = normalize_line(line)

        if not cleaned:
            continue

        lowered = cleaned.lower()

        if any(keyword in lowered for keyword in EDGE_CASE_KEYWORDS):
            edge_cases.append(cleaned)

    return sorted(set(edge_cases))


def build_implementation_plan(
    requirements: List[str],
    output_fields: List[str],
    edge_cases: List[str],
) -> List[str]:

    plan = [
        "Parse CLI arguments",
        "Validate input paths and arguments",
        "Read input file safely",
        "Implement required transformation/logic",
    ]

    if output_fields:
        plan.append(
            "Generate required output fields: "
            + ", ".join(output_fields)
        )

    if edge_cases:
        plan.append("Handle edge cases and invalid input")

    plan.extend(
        [
            "Print final output in required format",
            "Return correct exit codes",
        ]
    )

    return plan


def build_summary(
    purpose: str,
    requirements: List[str],
    output_fields: List[str],
    edge_cases: List[str],
    implementation_plan: List[str],
) -> str:

    sections = []

    sections.append("PURPOSE")
    sections.append(purpose)

    if requirements:
        sections.append("\nREQUIREMENTS")

        for item in requirements:
            sections.append(f"- {item}")

    if output_fields:
        sections.append("\nREQUIRED OUTPUT FIELDS")

        for field in output_fields:
            sections.append(f"- {field}")

    if edge_cases:
        sections.append("\nEDGE CASES")

        for case in edge_cases:
            sections.append(f"- {case}")

    if implementation_plan:
        sections.append("\nIMPLEMENTATION PLAN")

        for step in implementation_plan:
            sections.append(f"- {step}")

    return "\n".join(sections)


def create_plan(spec_text: str) -> PlanResult:
    purpose = extract_purpose(spec_text)

    requirements = extract_requirements(spec_text)

    output_fields = extract_output_fields(spec_text)

    edge_cases = extract_edge_cases(spec_text)

    implementation_plan = build_implementation_plan(
        requirements=requirements,
        output_fields=output_fields,
        edge_cases=edge_cases,
    )

    summary = build_summary(
        purpose=purpose,
        requirements=requirements,
        output_fields=output_fields,
        edge_cases=edge_cases,
        implementation_plan=implementation_plan,
    )

    return PlanResult(
        purpose=purpose,
        requirements=requirements,
        output_fields=output_fields,
        edge_cases=edge_cases,
        implementation_plan=implementation_plan,
        summary=summary,
    )


def summarize_spec(spec_text: str) -> str:
    plan = create_plan(spec_text)

    return plan.summary