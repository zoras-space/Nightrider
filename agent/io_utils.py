import sys
from agent.config_runtime import runtime_config

def info(message: str):
    if not runtime_config.strict_mode:
        print(message, file=sys.stderr)

def debug(message: str):
    if not runtime_config.strict_mode:
        print(message, file=sys.stderr)

def warning(message: str):
    print(message, file=sys.stderr)

def evaluator_output(message: str):
    print(message)
