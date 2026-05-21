# Nightrider

**An autonomous coding-agent framework for navigating hidden CLI specs through the night, one repair loop at a time.**

Nightrider is a lightweight Python framework for the hackathon reveal phase: read a hidden Markdown spec, plan a CLI solution, write code, run tests, inspect failures, repair, and keep timestamped evidence of the whole drive.

## Quick Start

Python version: **Python 3.10+**

```bash
cd nightrider
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

On Homebrew-managed Python, install dependencies inside the virtual environment above. Avoid `--break-system-packages`; it is not needed for this project.

## Running on Another Computer

Nightrider is portable. A new machine needs:

- Python 3.10+
- `pip` through Python's built-in packaging tools
- the packages in `requirements.txt`: `requests` and `pytest`
- Ollama only for real model-driven runs, not for mock smoke tests

From a fresh clone or copied project folder:

```bash
cd nightrider
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 agent/run_agent.py --init-logs
```

Verify the framework without Ollama or network access:

```bash
python3 agent/run_agent.py \
  --model mock-text-counter \
  --spec toy_specs/text_counter_spec.md \
  --program workspace/solution.py \
  --test-command "pytest toy_tests/test_text_counter.py -q" \
  --max-rounds 2
```

For real autonomous runs, install Ollama, pull the local model, and keep the server running:

```bash
ollama pull qwen2.5-coder:7b
ollama serve
```

The `bash Nightrider` launcher works from the project directory. A global `Nightrider` shell command is optional and machine-specific; the portable command is always `python3 agent/run_agent.py ...`.

Check readiness from the project directory:

```bash
python3 agent/run_agent.py --init-logs
python3 agent/run_agent.py --check-ollama
```

For the simplest operator experience, open the interactive console:

```bash
bash Nightrider
```

Inside the console, type `/help`. You can ask normal questions, run `/toy`, run `/hidden`, test the current program with `/program <args>`, check the model with `/check`, and start the dashboard with `/dashboard`.

For a no-network smoke test of the framework itself, use the built-in deterministic mock model:

```bash
python3 agent/run_agent.py \
  --model mock-text-counter \
  --spec toy_specs/text_counter_spec.md \
  --program workspace/solution.py \
  --test-command "pytest toy_tests/test_text_counter.py -q" \
  --max-rounds 2
```

## Night Drive Loop

The agent follows a simple autonomous loop:

1. Read the Markdown specification.
2. Extract CLI behavior, input format, output format, error handling, edge cases, constraints, and likely tests.
3. Create a focused implementation plan.
4. Generate or replace `workspace/solution.py` with a backup and change summary.
5. Run the configured test command.
6. Log stdout, stderr, exit code, command, duration, visible scores, and test results.
7. If tests fail, classify the failure as parsing, output format, exit code, runtime behavior, missing functionality, or unknown.
8. Request a targeted full-file patch and avoid repeating the same failed fix.
9. Repeat until tests pass, max rounds is reached, or repeated failures trigger a safe stop.
10. Write `agent_logs/final_report.md`.

## Toy Task Example

Use the toy specs to rehearse the workflow before the hidden reveal:

Each toy spec is a separate drill. Do not expect all toy test suites to pass against the same `workspace/solution.py` at the same time. Run the agent separately for each spec so it can regenerate the target program.

```bash
python3 agent/run_agent.py \
  --spec toy_specs/text_counter_spec.md \
  --program workspace/solution.py \
  --test-command "pytest toy_tests/test_text_counter.py -q" \
  --max-rounds 5
```

Terminal output is intentionally human-readable while full evidence stays in `agent_logs/`. Add `--verbose` for stdout/stderr and model summaries, or `--quiet` for minimal progress:

```bash
python3 agent/run_agent.py ... --verbose
python3 agent/run_agent.py ... --quiet
```

Other practice specs:

```bash
python3 agent/run_agent.py \
  --spec toy_specs/json_transformer_spec.md \
  --program workspace/solution.py \
  --test-command "pytest toy_tests/test_json_transformer.py -q" \
  --max-rounds 5

python3 agent/run_agent.py \
  --spec toy_specs/inventory_cli_spec.md \
  --program workspace/solution.py \
  --test-command "pytest toy_tests/test_inventory_cli.py -q" \
  --max-rounds 5
```

## Hidden Task Usage Template

After the hidden specification is released, operate the agent rather than manually writing the final program:

```bash
python3 agent/run_agent.py \
  --spec secret_spec/spec.md \
  --program workspace/solution.py \
  --test-command "python3 secret_spec/test_runner/run_tests.py --program 'python3 workspace/solution.py' --suite public" \
  --max-rounds 8
```

To use a different local model:

```bash
AGENT_MODEL=qwen2.5-coder:7b python3 agent/run_agent.py ...
```

or:

```bash
python3 agent/run_agent.py --model qwen2.5-coder:7b ...
```

## Repository Structure

```text
nightrider/
  README.md
  Nightrider
  agent_manifest.json
  requirements.txt
  agent/
    chat.py
    dashboard.py
    run_agent.py
    config.py
    logger.py
    terminal_ui.py
    model_client.py
    planner.py
    file_editor.py
    command_runner.py
    repair_loop.py
    report_writer.py
    prompts.py
  workspace/
    solution.py
  toy_specs/
  toy_tests/
  agent_logs/
```

## Local Dashboard

Start the lightweight status UI in one terminal:

```bash
python3 agent/dashboard.py --port 8765
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765), then run the agent in another terminal. The dashboard refreshes every 2 seconds and shows latest test runs, commands, decisions, errors, human interventions, final report, and the current `workspace/solution.py`.

## Architecture Overview

Nightrider is a local autonomous coding-agent pipeline. `run_agent.py` parses the reveal-time command, `planner.py` turns the spec into a concise summary and implementation plan, `model_client.py` calls a local Ollama `/api/generate` endpoint, and `repair_loop.py` coordinates generation, test execution, failure analysis, and full-file repairs. `file_editor.py` backs up the previous solution before replacement, `logger.py` records timestamped prompts, decisions, commands, test runs, errors, and human interventions, and `dashboard.py` provides a local read-only view of those logs while the loop runs.

## Logging and Compliance

All required log files are created under `agent_logs/`:

- `prompts.log`
- `decisions.log`
- `commands.log`
- `test_runs.log`
- `errors.log`
- `human_interventions.log`
- `final_report.md`

Every log entry includes a timestamp like `[2026-05-21 20:18:03]`.

Manual interventions after reveal should be recorded immediately. Every post-reveal human intervention belongs in `agent_logs/human_interventions.log`:

```bash
python3 agent/run_agent.py --log-human-intervention "Installed pytest because tests could not run. No final program code was edited manually."
```

If there are no interventions, `human_interventions.log` remains present and says:

```text
No human interventions logged yet.
```

## Allowed Model Disclosure

Default model: `qwen2.5-coder:7b`

Provider: local Ollama at `http://localhost:11434/api/generate`

This repo does not include paid API clients, API keys, Copilot integration, paid IDE assistant assumptions, or institutional quota usage. After the hidden spec release, the intended workflow is local/open-model operation only.

## 19:45 Checkpoint

Before the reveal or at the required checkpoint time, commit and tag the prepared framework:

```bash
git add .
git commit -m "Agent readiness checkpoint"
git tag agent-readiness-1945
git push --follow-tags
```

Reference this tag in the final submission README/report. If the exact tag name changes, note the actual commit hash and tag in `agent_logs/final_report.md`.

## Reproducing Public Test Runs

Activate the project environment before running smoke tests:

```bash
cd nightrider
source .venv/bin/activate
```

Required readiness smoke checks:

```bash
python3 -m py_compile agent/*.py workspace/solution.py toy_tests/*.py

pytest toy_tests/test_text_counter.py -q

python3 agent/run_agent.py \
  --model mock-text-counter \
  --spec toy_specs/text_counter_spec.md \
  --program workspace/solution.py \
  --test-command "pytest toy_tests/test_text_counter.py -q" \
  --max-rounds 2
```

Toy tests can be reproduced with:

```bash
pytest toy_tests/test_text_counter.py -q
pytest toy_tests/test_json_transformer.py -q
pytest toy_tests/test_inventory_cli.py -q
```

Hidden public tests should be reproduced with the command provided by the challenge organizers, for example:

```bash
python3 secret_spec/test_runner/run_tests.py --program 'python3 workspace/solution.py' --suite public
```

## Final Submission Checklist

- `README.md` includes run command, Python version, install steps, architecture, checkpoint reference, and test reproduction notes.
- `agent_manifest.json` discloses local model/provider usage.
- `workspace/solution.py` contains the final generated program.
- `agent_logs/` contains timestamped prompts, decisions, commands, tests, errors, interventions, and final report.
- No paid model credentials or secret keys are present.
- Human interventions after reveal, if any, are logged.

## Presentation Notes

For judges, emphasize the workflow evidence: the agent reads the spec, generates a plan, writes code, runs tests, repairs failures, and preserves logs. The final program matters, but the core project is the calm, repeatable Night Drive Loop that makes each autonomous decision inspectable.
