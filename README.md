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

Final public readiness status:
- Framework smoke tests passing
- Autonomous repair loop operational
- Logging system operational

---

## Known Limitations

- Real autonomous generation requires a local Ollama instance.
- Toy specs are independent and should not be expected to pass simultaneously with the same generated solution.
- Hidden-spec performance depends on local model quality and reveal-time task complexity.
- Extremely large specs or long-running test suites may require increased iteration limits.

---

## Readiness Checkpoint Reference

Checkpoint tag: `agent-readiness-1945`