IMPORTANT_REQUIREMENT_KEYWORDS = [
    "must",
    "required",
    "include",
    "json",
    "field",
    "output",
    "edge case",
]


def extract_requirements(spec_text: str) -> list[str]:
    requirements = []

    for line in spec_text.splitlines():
        lowered = line.lower()

        if any(keyword in lowered for keyword in IMPORTANT_REQUIREMENT_KEYWORDS):
            requirements.append(line.strip())

    return requirements