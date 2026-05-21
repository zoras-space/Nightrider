from agent.command_runner import run_command
from agent.io_utils import info

def run_repair_loop(
    model_client,
    test_command: str,
    max_iterations: int,
    timeout: int,
):
    for iteration in range(max_iterations):
        info(f"iteration {iteration + 1}")

        result = run_command(
            test_command,
            timeout=timeout,
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "tests_passed": True,
                "iterations": iteration + 1,
            }

        prompt = (
            "Tests failed.\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

        model_client.generate(prompt)

    return {
        "status": "failure",
        "tests_passed": False,
        "iterations": max_iterations,
    }
