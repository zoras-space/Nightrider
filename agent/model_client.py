import requests
from agent.fallback_strategy import DeterministicFallback

class OllamaClient:
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "top_p": 1,
                    "seed": 42,
                },
            },
            timeout=120,
        )

        response.raise_for_status()
        return response.json().get("response", "")

def get_model_client(config):
    if config.offline_mode:
        return DeterministicFallback()

    try:
        return OllamaClient(
            model=config.model,
            base_url=config.ollama_url,
        )
    except Exception:
        return DeterministicFallback()
