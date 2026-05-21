from pathlib import Path

def ensure_log_directory(enabled: bool):
    if not enabled:
        return None

    log_dir = Path("agent_logs")
    log_dir.mkdir(exist_ok=True)

    return log_dir
