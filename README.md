# Nightrider

**An autonomous coding-agent framework for navigating hidden CLI specs through the night, one repair loop at a time.**

Nightrider is a lightweight autonomous repair-loop framework that reads hidden Markdown specifications, plans implementations, generates code, runs tests, repairs failures, and logs every decision for reproducibility and judging.

---

## Final Command

```bash
python3 knit.py compile <input_file>
```

Example:

```bash
python3 knit.py compile secret_spec/spec.md
```

The command launches the autonomous compile/repair workflow and writes logs and artifacts into `agent_logs/`.

---

## Setup

Python version: **Python 3.10+**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional local model setup for autonomous runs:

```bash
ollama pull qwen2.5-coder:7b
ollama serve
```

---

## Agent Overview

Nightrider is a local autonomous coding-agent pipeline.

- `knit.py` provides the official competition CLI entrypoint.
- `run_agent.py` orchestrates the repair loop.
- `planner.py` extracts requirements and implementation plans from specs.
- `model_client.py` communicates with local Ollama models.
- `repair_loop.py` handles generation, testing, failure analysis, and retries.
- `logger.py` records prompts, commands, errors, decisions, and interventions.
- `dashboard.py` provides a lightweight local monitoring UI.

The system operates in iterative rounds:

1. Read spec
2. Plan implementation
3. Generate code
4. Run tests
5. Analyze failures
6. Repair and retry
7. Produce final logs and report

---

## Public Test Run

Smoke test command:

```bash
python3 knit.py compile toy_specs/text_counter_spec.md
```

Additional verification:

```bash
pytest toy_tests/test_text_counter.py -q
pytest toy_tests/test_json_transformer.py -q
pytest toy_tests/test_inventory_cli.py -q
```

Current readiness status:

- Autonomous repair loop operational
- Failure detection operational
- Retry pipeline operational
- Logging system operational
- Local CLI entrypoint operational

---

## Known Limitations

- Real autonomous generation requires a local Ollama instance.
- Toy specs are independent and should not be expected to pass simultaneously with the same generated solution.
- Hidden-spec performance depends on local model quality and reveal-time task complexity.
- Extremely large specs or long-running test suites may require increased iteration limits.
- Repeated identical failures trigger escalation logic but may still require improved prompting.

---

## Readiness Checkpoint Reference

Checkpoint tag: `agent-readiness-1945`

---

## Running on Another Computer

Nightrider is portable. A new machine needs:

- Python 3.10+
- `pip`
- Dependencies from `requirements.txt`
- Ollama only for real model-driven runs

```bash
cd nightrider
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 agent/run_agent.py --init-logs
```

---

## Repository Structure

```text
nightrider/
  README.md
  knit.py
  requirements.txt
  agent_manifest.json
  agent/
  workspace/
  toy_specs/
  toy_tests/
  secret_spec/
  agent_logs/
```

---

## Logging and Compliance

All required log files are created under `agent_logs/`:

- `prompts.log`
- `decisions.log`
- `commands.log`
- `test_runs.log`
- `errors.log`
- `human_interventions.log`
- `final_report.md`

Every log entry includes timestamps.

---

## Final Submission Checklist

- `README.md` includes command, setup, architecture, tests, and checkpoint reference.
- `knit.py` provides the required competition command shape.
- `agent_manifest.json` discloses local model usage.
- `workspace/solution.py` contains the generated solution.
- `agent_logs/` contains prompts, decisions, commands, tests, errors, interventions, and final report.
- No paid API keys or secrets are included.