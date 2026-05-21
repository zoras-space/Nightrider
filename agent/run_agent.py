#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from agent.config_runtime import runtime_config
from agent.io_utils import info
from agent.json_output import emit_json
from agent.logging_utils import ensure_log_directory
from agent.model_client import get_model_client
from agent.repair_loop import run_repair_loop

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("spec_positional", nargs="?")

    parser.add_argument("--spec")
    parser.add_argument("--test-command", required=True)

    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--write-logs", action="store_true")

    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=60)

    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--ollama-url", default="http://localhost:11434")

    return parser.parse_args()

def main():
    args = parse_args()

    runtime_config.strict_mode = args.strict
    runtime_config.json_output = args.json_output
    runtime_config.offline_mode = args.offline
    runtime_config.write_logs = args.write_logs

    runtime_config.max_iterations = args.max_iterations
    runtime_config.timeout = args.timeout

    runtime_config.model = args.model
    runtime_config.ollama_url = args.ollama_url

    spec_path = args.spec or args.spec_positional

    if not spec_path:
        print("missing specification", file=sys.stderr)
        sys.exit(2)

    if not Path(spec_path).exists():
        print("specification not found", file=sys.stderr)
        sys.exit(2)

    ensure_log_directory(runtime_config.write_logs)

    info("starting agent")

    model_client = get_model_client(runtime_config)

    result = run_repair_loop(
        model_client=model_client,
        test_command=args.test_command,
        max_iterations=runtime_config.max_iterations,
        timeout=runtime_config.timeout,
    )

    if runtime_config.json_output:
        emit_json(result)
    else:
        print(result["status"])

    sys.exit(0 if result["status"] == "success" else 1)

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        sys.exit(130)

    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
