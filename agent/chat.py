"""Interactive Nightrider operator console."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from urllib import request

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import logger  # noqa: E402
from agent.config import resolve_model  # noqa: E402
from agent.model_client import OllamaClient  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HIDDEN_COMMAND = (
    "python3 secret_spec/test_runner/run_tests.py "
    "--program 'python3 workspace/solution.py' --suite public"
)
PYTHON = shlex.quote(sys.executable)
TOY_TEST_COMMAND = f"{PYTHON} -m pytest toy_tests/test_text_counter.py -q"
ACTIVE_MODEL = "qwen2.5-coder:7b"


SYSTEM_CONTEXT = """You are Nightrider's local operator assistant.
Help the user run and understand this autonomous coding-agent project.
Do not suggest paid model tools for post-reveal work.
Keep answers concise, practical, and focused on commands, logs, tests, and the current program.
If the user asks you to solve the hidden challenge manually, remind them to operate the agent workflow instead.
"""


def run_live(command: str) -> int:
    print(f"\n[Nightrider] running: {command}\n", flush=True)
    completed = subprocess.run(command, shell=True, cwd=ROOT, text=True)
    print(f"\n[Nightrider] command exited with code {completed.returncode}\n")
    return completed.returncode


def run_capture(command: str) -> None:
    print(f"\n[Nightrider] running: {command}\n", flush=True)
    completed = subprocess.run(command, shell=True, cwd=ROOT, text=True, capture_output=True)
    if completed.stdout:
        print("stdout:")
        print(completed.stdout.rstrip())
    if completed.stderr:
        print("stderr:")
        print(completed.stderr.rstrip())
    print(f"exit_code: {completed.returncode}\n")


def start_dashboard() -> None:
    if dashboard_is_running():
        print("[Nightrider] Dashboard is already running: http://127.0.0.1:8765")
        return
    command = [sys.executable, "agent/dashboard.py", "--port", "8765"]
    log_path = ROOT / "agent_logs" / "dashboard_server.log"
    logger.ensure_log_files()
    with log_path.open("a", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
        )
    logger.log_decision(f"Started dashboard from interactive console with PID {process.pid}.")
    print("[Nightrider] Dashboard started: http://127.0.0.1:8765")
    print(f"[Nightrider] Server log: {log_path}")


def dashboard_is_running() -> bool:
    try:
        with request.urlopen("http://127.0.0.1:8765/api/status", timeout=1):
            return True
    except Exception:  # noqa: BLE001
        return False


def print_help() -> None:
    print(
        """
Nightrider console commands:

  /help                  Show this help.
  /check                 Check local Ollama/model readiness.
  /logs                  Create required log files.
  /dashboard             Start the local dashboard on http://127.0.0.1:8765.
  /toy                   Run the text-counter toy agent loop.
  /hidden                Run the default hidden-spec agent command.
  /hidden <spec> <cmd>   Run a custom hidden-spec path and quoted test command.
  /program <args>        Run python3 workspace/solution.py with arguments.
  /test                  Run python -m pytest toy_tests/test_text_counter.py -q.
  /quit                  Exit.

Anything else is sent to the local Ollama model as a chat-style question.
""".strip()
    )


def chat_response(client: OllamaClient, history: list[str], user_text: str) -> str:
    history_text = "\n\n".join(history[-8:])
    prompt = (
        f"{SYSTEM_CONTEXT}\n\n"
        f"Recent conversation:\n{history_text or '<none>'}\n\n"
        f"User: {user_text}\n"
        "Nightrider:"
    )
    logger.log_prompt(f"CHAT\n{prompt}")
    response = client.generate(prompt).text
    logger.log_decision(f"CHAT_RESPONSE\n{response}")
    return response


def handle_command(text: str) -> bool:
    if text in {"/quit", "/exit"}:
        return False
    if text == "/help":
        print_help()
        return True
    if text == "/logs":
        logger.ensure_log_files()
        logger.log_decision("Interactive console initialized required log files.")
        print("[Nightrider] Agent logs initialized.")
        return True
    if text == "/check":
        run_live(f"{PYTHON} agent/run_agent.py --model {shlex.quote(ACTIVE_MODEL)} --check-ollama")
        return True
    if text == "/dashboard":
        start_dashboard()
        return True
    if text == "/toy":
        run_live(
            f"{PYTHON} agent/run_agent.py "
            f"--model {shlex.quote(ACTIVE_MODEL)} "
            "--spec toy_specs/text_counter_spec.md "
            "--program workspace/solution.py "
            f"--test-command {shlex.quote(TOY_TEST_COMMAND)} "
            "--max-rounds 5"
        )
        return True
    if text == "/hidden":
        run_live(
            f"{PYTHON} agent/run_agent.py "
            f"--model {shlex.quote(ACTIVE_MODEL)} "
            "--spec secret_spec/spec.md "
            "--program workspace/solution.py "
            f"--test-command {shlex.quote(DEFAULT_HIDDEN_COMMAND)} "
            "--max-rounds 8"
        )
        return True
    if text.startswith("/hidden "):
        parts = shlex.split(text)
        if len(parts) < 3:
            print('[Nightrider] Usage: /hidden <spec-path> "<test command>"')
            return True
        spec_path = parts[1]
        test_command = " ".join(parts[2:])
        run_live(
            f"{PYTHON} agent/run_agent.py "
            f"--model {shlex.quote(ACTIVE_MODEL)} "
            f"--spec {shlex.quote(spec_path)} "
            "--program workspace/solution.py "
            f"--test-command {shlex.quote(test_command)} "
            "--max-rounds 8"
        )
        return True
    if text.startswith("/program"):
        args = text.removeprefix("/program").strip()
        command = f"{PYTHON} workspace/solution.py"
        if args:
            command += f" {args}"
        run_capture(command)
        return True
    if text == "/test":
        run_live(TOY_TEST_COMMAND)
        return True
    print("[Nightrider] Unknown slash command. Type /help.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Open the Nightrider interactive operator console.")
    parser.add_argument("--model", help="Ollama model name. Overrides AGENT_MODEL.")
    parser.add_argument("--ollama-url", default="http://localhost:11434/api/generate")
    args = parser.parse_args()

    logger.ensure_log_files()
    model = resolve_model(args.model)
    global ACTIVE_MODEL
    ACTIVE_MODEL = model
    client = OllamaClient(model=model, endpoint=args.ollama_url)
    history: list[str] = []

    print("Nightrider interactive console")
    print(f"Model: {model}")
    print("Type /help for commands, /quit to exit.\n")

    while True:
        try:
            text = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Nightrider] Console closed.")
            return 0
        if not text:
            continue
        if text.startswith("/"):
            if not handle_command(text):
                print("[Nightrider] Console closed.")
                return 0
            continue

        try:
            response = chat_response(client, history, text)
        except Exception as exc:  # noqa: BLE001
            logger.log_error(f"Interactive chat failed: {exc}")
            print(f"[Nightrider] Chat failed: {exc}")
            continue
        print(f"\nnightrider > {response}\n")
        history.append(f"User: {text}\nNightrider: {response}")


if __name__ == "__main__":
    raise SystemExit(main())
