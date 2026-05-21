Agent report · MDCopyAgent Architecture Report
Nightrider — Hackathon Submission

1. Models & Why
   Primary: qwen2.5-coder:7b via Ollama
   Why: Purpose-built for code generation. Understands Python, CLI tools, JSON schemas,
   and test-driven iteration better than general models at the same size. Fast enough to run
   many iterations overnight on consumer hardware.
   Secondary: llama3.1:8b via Ollama
   Why: Used as a reviewer/critic, not a generator. After Qwen produces a patch,
   Llama reads the test failure + the patch and answers one question: "does this fix make
   sense, or does it introduce a new problem?" Separation of generator vs reviewer catches
   a class of confident-but-wrong outputs that self-review misses.
   Why not a frontier model?
   The rules prohibit paid models after 20:00. Beyond compliance, engineering around
   weaker models is the actual challenge — prompt discipline, tight feedback loops, and
   structured output matter more here than raw model capability.

2. Tools Available to the Agent & Why
   ToolWhyread_file(path)Reads spec, source files, test outputwrite_file(path, content)Creates and patches solution.pyrun_shell(cmd)Runs tests, git commands, installs depsrun_tests()Shortcut: runs public suite, returns structured score + failuresgit_commit(msg)Preserves every iteration; judges read historyappend_log(file, entry)Writes timestamped entries to all 7 agent_logs/ filessearch_in_file(path, pattern)Locates relevant sections without reading full files
   Why this set: Every tool maps directly to a step in the implementation loop.
   No tool does anything the agent shouldn't do autonomously (no browser, no external APIs).
   The agent cannot accidentally commit secrets because write_file validates paths against
   a whitelist.

3. Agent Architecture
   ┌─────────────────────────────────────────────────────┐
   │ ORCHESTRATOR │
   │ (Python script: agent.py) │
   └────────────────────────┬────────────────────────────┘
   │ controls loop
   ┌──────────────▼──────────────┐
   │ PLAN PHASE │
   │ read spec → make plan → │
   │ write decisions.log │
   └──────────────┬──────────────┘
   │
   ┌──────────────▼──────────────┐
   │ IMPLEMENT PHASE │ ◄─────┐
   │ Qwen generates code patch │ │
   │ write_file(solution.py) │ │
   └──────────────┬──────────────┘ │
   │ │
   ┌──────────────▼──────────────┐ │
   │ TEST PHASE │ │
   │ run public test suite │ │
   │ parse score + failures │ │
   └──────────────┬──────────────┘ │
   │ │
   ┌─────────▼────────┐ │
   │ score == 100% ? │ │
   └──┬───────────────┘ │
   │ NO │
   ┌───────▼───────────────┐ │
   │ REVIEW PHASE │ │
   │ Llama reads failure │ │
   │ + patch, gives verdict │
   └───────┬───────────────┘ │
   │ │
   ┌───────▼───────────────┐ │
   │ PATCH PROMPT PHASE │──────────────┘
   │ Qwen writes fix │
   │ git commit iteration │
   └───────────────────────┘
   │ YES (100%)
   ┌───────▼───────────────┐
   │ DONE — final commit │
   │ update final_report │
   └───────────────────────┘
   Loop behaviour

Max iterations: 30 (safety cap)
On stuck loop (same score 3 iterations): escalate prompt, force different approach
On crash: log to errors.log, retry with simplified prompt
Every iteration: git commit + all logs updated

Prompt structure (sent to Qwen each iteration)
SYSTEM: You are a competition programmer. Output ONLY valid Python. No explanation.
No markdown fences. No comments unless they aid correctness.

SPEC SUMMARY: {compressed spec — key rules only}

CURRENT solution.py: {full file}

FAILING TESTS:
{test name} — expected: {expected} — got: {actual}

TASK: Patch solution.py to fix the failing tests. Output the complete corrected file.
Why compressed spec: 7b models have limited context. Sending the full spec every
iteration wastes tokens and degrades output quality. The orchestrator extracts the
relevant rules for failing test categories only.

4. Test Strategy
   Layers

Public suite (secret_spec/test_runner/run_tests.py --suite public)
Run after every code change. Primary signal for the loop.
Regression guard — before applying a patch, run tests. If score goes down,
discard the patch and re-prompt with "previous patch made things worse."
Self-generated edge cases — after passing all public tests, Qwen generates
5 additional edge cases based on the spec. These are NOT used to grade; they probe
corner cases the hidden tests likely target (combined rules, boundary values, empty
inputs, unicode, large inputs).
Diff review — Llama reviews the git diff before final commit and flags anything
that looks like hardcoded outputs or test-specific hacks.

What we never do

Generate expected outputs using our own solution (the rules explicitly forbid this)
Use the hidden test runner output to guide implementation
Modify the test runner

5. Human Intervention Level
   Target: zero after 20:00.
   Before reveal (allowed freely)

Building agent infrastructure
Installing Ollama + models
Testing the loop on toy tasks
Tuning prompts

After reveal (logged if it happens)
ScenarioActionAgent crashes mid-loopRestart agent, log itOllama model hangsKill and restart Ollama, log itMissing Python dependencypip3 install <pkg>, log itAgent stuck in loop 10+ iterationsEdit orchestrator prompt, log itChoose between two agent outputsPick better one, log the choice
What humans never do after reveal

Edit solution.py directly
Write any logic manually
Copy solutions from external sources

Logging guarantee
Every human action after 20:00 gets a timestamped entry in human_interventions.log
within 2 minutes of happening. The log is append-only during the run.

6. solve() Architecture in solution.py
   The hidden spec is unknown, but the pipeline is designed to be swapped without
   touching anything except solve() and optionally parse_input():
   read_input() → parse_input() → solve() → format_output() → write_output()
   solve() is the only function the agent rewrites. Everything else — CLI, I/O,
   error handling, exit codes, logging — is stable infrastructure the agent inherits
   and does not touch.
   This means:

Agent prompts can say "rewrite only the solve() function"
Shorter context = better outputs from 7b models
Regressions in I/O handling are impossible if the agent stays in its lane
