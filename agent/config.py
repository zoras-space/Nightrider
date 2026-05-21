from dataclasses import dataclass

@dataclass
class AgentConfig:
    strict_mode: bool = False
    json_output: bool = False
    offline_mode: bool = False
    write_logs: bool = False

    temperature: float = 0.0
    top_p: float = 1.0
    seed: int = 42

    max_iterations: int = 10
    timeout: int = 60

    model: str = "qwen2.5-coder:7b"
    ollama_url: str = "http://localhost:11434"
