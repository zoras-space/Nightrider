"""Local Ollama client for free-model-friendly code generation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import parse, request
from urllib.error import HTTPError, URLError

from agent.config import DEFAULT_OLLAMA_URL


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model: str


class OllamaClient:
    """Small HTTP client for Ollama's /api/generate endpoint."""

    def __init__(self, model: str, endpoint: str = DEFAULT_OLLAMA_URL, timeout_seconds: int = 180) -> None:
        self.model = model
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> ModelResponse:
        if self.model == "mock-text-counter":
            return ModelResponse(text=_mock_text_counter_response(prompt), model=self.model)
        if self.model == "mock-repair-drill":
            return ModelResponse(text=_mock_repair_drill_response(prompt), model=self.model)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            },
        }
        data = self._post_json(payload)
        return ModelResponse(text=data.get("response", "").strip(), model=self.model)

    def check_available(self) -> tuple[bool, str]:
        """Return whether Ollama is reachable and a short status message."""

        tags_url = _ollama_tags_url(self.endpoint)
        try:
            with request.urlopen(tags_url, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            return False, f"Could not reach Ollama at {tags_url}: {exc}"

        models = [item.get("name", "") for item in data.get("models", [])]
        if self.model in models:
            return True, f"Ollama is reachable and model '{self.model}' is installed."
        if models:
            return False, (
                f"Ollama is reachable, but model '{self.model}' was not found. "
                f"Installed models: {', '.join(models)}"
            )
        return False, f"Ollama is reachable, but no models are installed. Pull '{self.model}'."

    def _post_json(self, payload: dict) -> dict:
        """POST JSON using the standard library so setup stays lightweight."""

        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(
                "Could not reach Ollama at "
                f"{self.endpoint}. Start it with 'ollama serve' and ensure the model is pulled."
            ) from exc


def _ollama_tags_url(generate_endpoint: str) -> str:
    parsed = parse.urlparse(generate_endpoint)
    return parse.urlunparse((parsed.scheme, parsed.netloc, "/api/tags", "", "", ""))


def _mock_text_counter_response(prompt: str) -> str:
    """Deterministic local test double for validating the agent loop."""

    if "Return only the complete Python source" not in prompt:
        if "implementation plan" in prompt.lower():
            return (
                "Use argparse-style validation, read the UTF-8 file, compute splitlines, "
                "split word count, character length, print compact JSON, and return nonzero on errors."
            )
        return (
            "The program accepts one file path, reads UTF-8 text, prints JSON with line_count, "
            "word_count, and char_count, keeps stdout clean, and reports argument/read errors to stderr."
        )

    return '''\
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: solution.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"could not read file: {exc}", file=sys.stderr)
        return 1

    result = {
        "line_count": len(text.splitlines()),
        "word_count": len(text.split()),
        "char_count": len(text),
    }
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _mock_repair_drill_response(prompt: str) -> str:
    """Deterministic test double that fails once, then repairs the drill field."""

    if "Return only the complete" not in prompt:
        return (
            "The CLI accepts one UTF-8 file path and must output JSON with line_count, "
            "word_count, char_count, and nonempty_line_count. Errors go to stderr."
        )
    if "Failure analysis:" not in prompt:
        return '''\
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: solution.py <path>", file=sys.stderr)
        return 2
    try:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"could not read file: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "line_count": len(text.splitlines()),
        "word_count": len(text.split()),
        "char_count": len(text),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    return '''\
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: solution.py <path>", file=sys.stderr)
        return 2
    try:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"could not read file: {exc}", file=sys.stderr)
        return 1

    lines = text.splitlines()
    print(json.dumps({
        "line_count": len(lines),
        "word_count": len(text.split()),
        "char_count": len(text),
        "nonempty_line_count": sum(1 for line in lines if line.strip()),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
