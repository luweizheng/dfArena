# PrepBench in dfArena

This directory contains curated workload tasks, a local simulator for clarifying underspecified queries, and the generation and evaluation workflow. See [PREPBENCH_LICENSE](PREPBENCH_LICENSE) for the source license.

Task curation replaces Tableau-specific instructions in PrepBench with DataFrame workflows and describes the supplied CSV assets as input files, with corresponding updates to knowledge-base references. Visualization-only instructions are removed while data-processing requirements and the original ambiguities are retained.

Historical migration records remain in the local `curation/` directory; they are not runtime dependencies or part of this release. The current evaluation protocol is defined in [evaluation/README.md](../evaluation/README.md).

## Installation and execution

Use Python 3.11+ on the host and run these commands from the dfArena repository root:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
docker build -f docker/agent-sandbox.Dockerfile -t dfarena-agent-sandbox:latest .
```

Run the complete workflow:

```bash
.venv/bin/python PrepBench/scripts/run_benchmark.py \
  --case 001 --mode clarified --backend pandas \
  --model gpt-6-astra --image dfarena-agent-sandbox:latest

.venv/bin/python PrepBench/scripts/run_benchmark.py \
  --case 005 --mode interact --backend polars \
  --model gpt-6-astra --image dfarena-agent-sandbox:latest
```

The default image is `dfarena-agent-sandbox:latest`; keep the image fixed for comparative experiments. `--mode` defaults to `interact` and supports `direct`, `interact`, and `clarified`. `--backend` supports pandas, polars, ibis with DuckDB backend, and pyspark. PySpark uses a local SparkSession. `--model` overrides the model. `--agent` supports Codex and OpenCode. Reasoning effort comes from the configuration selected by `--codex-config-dir`, which defaults to `runners/configs/codex`.

## Experimental modes

The three modes represent different query and user-interaction conditions:

- `direct`: The agent sees only the original `query.md`, without additional explanation, and cannot request clarification. This measures DataFrame program generation from the initial natural-language request.
- `clarified`: The agent receives the manually curated complete requirements in `query_full.md` and cannot request clarification. This provides a reference condition with explicit requirements.
- `interact`: The agent receives the same `query.md` as in `direct`, but can ask the simulated user questions while solving the task. The agent must identify ambiguities, formulate questions, and use the answers to clarify the requirements.

`clarified` and `interact` use the same underlying complete task specification: the former provides it upfront, while the latter allows the agent to obtain clarifications through limited interaction. Comparisons across the modes help distinguish the effects of initial requirement understanding, interactive clarification, and implementation. All three modes use the same input data, target outputs, and evaluation protocol.

## Interact protocol

An `interact` run follows this call chain:

```text
agent reads query.md and inputs
  → identifies uncertainty in the requirements
  → calls the MCP clarification.ask([question, ...]) tool
  → the simulator acts like a human user and answers business-rule questions using the hidden complete requirements
  → the agent uses the answers to write and execute solution.py
  → the evaluator compares the output CSV with the ground truth
```

The simulator acts as an **oracle user simulator**. It can read `query_full.md`, `amb_kb.json`, and the reference solution internally to recover the predefined business rules. These files and their code are not returned directly to the agent; the agent receives natural-language answers to its questions. The simulator is instructed to refuse requests for raw-data inspection, example outputs, hidden specifications, or implementation code.

The simulator is itself an LLM-backed service. For each clarification request from the coding agent, it builds a prompt from the agent's questions and the hidden task materials, then sends that prompt to the configured LLM provider to generate the simulated user's answer. This introduces a second model-serving dependency in an `interact` run, separate from the coding agent's own model request. Provider or API failures, connection failures, and timeouts are recorded as simulator errors and cause `/session/ask` to return HTTP 502. If the provider responds successfully but the response is invalid JSON or violates the answer contract, the simulator retries once with validation feedback; a second invalid response becomes a refusal for the affected questions.

By default, each session counts at most 3 successfully processed rounds, and each round accepts at most 10 questions. The total question budget is based on the number of ambiguity entries in `amb_kb.json`:

```text
max_questions = min(ceil(2.5 × ambiguity_count), max(25, ambiguity_count))
```

The budget and usage counters are stored in the simulator’s internal session state. `interaction.ask_calls` counts logged HTTP requests, not questions. Complete requests, answers, classifications, and provenance are stored in `logs/interaction.jsonl`; the response exposed to the agent contains only questions and answers.

Request validation failures and exceptions from simulator calls do not consume round or question budgets. Once a session reaches its round or question limit, subsequent requests receive a quota-reached message. The number of HTTP requests can therefore exceed 3, although no more than 3 successfully processed rounds are counted.

Simulator responses are not the benchmark’s final correctness labels; correctness is determined later by the table evaluator. If the simulator model returns invalid JSON or violates the answer contract, the simulator retries once with validation feedback. If the second response is still invalid, it returns a refusal for each expected question. Provider/API failures, timeouts, and connection errors are different: they are recorded as errors and `/session/ask` returns HTTP 502 rather than converting the failure into a refusal. Simulator failures can be investigated through `interaction.jsonl` and `server.log`; agent tool-call and code-generation failures are recorded in the agent log and generation/evaluation stage records.

## Script responsibilities

- `run_benchmark.py`: Allocates a run directory and invokes `generate.py` followed by `evaluate.py`. A generation failure records `evaluation.status=skipped`. An evaluated run exits with status 0 only if evaluation passes; otherwise it exits with status 1.
- `generate.py`: Provides the selected query and input data to the isolated agent, which generates and executes DataFrame code for the workload, then saves the generation records. In `direct`, the agent receives the original `query.md` and no simulator is started. In `clarified`, it receives the complete requirements from `query_full.md` and no simulator is started. In `interact`, it receives the original `query.md` and can ask the simulator for clarification while generating the DataFrame code.
- `evaluate.py`: Reads the case configuration, ground truth, and candidate output; calls the shared root-level `evaluation/` module; and saves the full report and evaluation summary. It does not execute agent code.
- `runners/results.py`: Shared stage-record writing, token aggregation, and `result.json` reconstruction for PrepBench and DataAgentBench.
- `runners/timed_process.py`: Shared wrapper for timing the agent process inside the container.

Run generation and evaluation separately:

```bash
.venv/bin/python PrepBench/scripts/generate.py \
  --case 001 --mode clarified --backend pandas --image dfarena-agent-sandbox:latest

# Use the RUN path printed by the preceding command; this path is an example.
.venv/bin/python PrepBench/scripts/evaluate.py \
  --case 001 \
  --run-dir PrepBench/case_001/runs/clarified/codex_gpt-6-astra/pandas/r001
```

Standalone evaluation checks the task and status in `generation.json`. Re-evaluation preserves the generation record while updating `evaluation.json` and the summary. The lower-level `python -m evaluation` command can compare arbitrary CSV files but does not automatically update run summaries. See [evaluation/README.md](../evaluation/README.md) for the configuration and comparison protocol.

## Directory layout and results

```text
PrepBench/
  scripts/
    run_benchmark.py
    generate.py
    evaluate.py
    simulator_server.py
    simulator/
    tests/
  case_XXX/
    inputs/
    query.md
    query_full.md
    amb_kb.json
    reference/solution.py
    evaluation/config.json
    evaluation/gt/output_*.csv
    runs/<mode>/<agent-model>/<backend>/r001/
      result.json
      detail/
        generation.json
        evaluation.json          # after evaluation starts
        agent_exec_timing.json
        prompt.txt
        command.json
        codex_sessions/          # Codex, when archived
        opencode_sessions/       # OpenCode, when archived
      logs/
        agent_events.jsonl
        agent_stderr.log
        server.log               # interact
        interaction.jsonl        # interact
      assets.json
      session.json               # interact
      workspace/
        mcp_stderr.log           # interact
        solution.py
        outputs/output_*.csv
```

Run numbers increase independently for each mode/model/backend combination; concurrent run-number allocation is not implemented. New runs no longer write `run.json`, and old runs are not migrated automatically. The run directory supplied to `generate.py` must be empty to prevent stale answers or evaluation results from being reused.

`detail/generation.json` records the model, mode, backend, generation status, timing, token usage, output paths, and interaction details. `detail/evaluation.json` records evaluation timing, `status`, `passed`, error types, and the complete evaluator result under `report`, including configuration, ground-truth, and candidate hashes. `result.json` summarizes the key metrics and can be rebuilt from whichever stage files are present. JSON stage records are written through temporary files followed by replacement; the stage records are retained.

A generation status of `completed` means only that the agent exited normally and produced `solution.py` and CSV output; it does not imply correctness. When evaluation has not run or is skipped, `passed=null`. A candidate comparison failure sets `passed=false`. A ground-truth, configuration, or evaluator error sets `status=error` and `passed=null`, with the underlying report retained.

## Timing and token usage

Generation `started_at` and `finished_at` are UTC ISO 8601 timestamps. `elapsed_seconds` uses a monotonic clock inside the container, starting immediately before the selected agent process launches and stopping after it exits or is terminated on timeout. It excludes Docker startup, simulator startup, cleanup, and evaluation. It includes agent exploration, code execution and repair, and simulator waits. It is not the standalone execution time of `solution.py`. Missing timing reports remain `null`. Reports are retained for ordinary failures and timeouts, but may be missing after a forced container termination.

For Codex, `token_usage` aggregates valid `turn.completed.usage` events and includes `input_tokens`, `output_tokens`, `cached_input_tokens`, and `total_tokens` (input plus output, without counting cached input twice). Missing values are `null`; `token_usage_status` is `complete`, `partial`, or `unavailable`. Simulator tokens are excluded, and unreported usage from interrupted requests cannot be recovered.

The `interaction` summary includes `enabled` and `ask_calls`. `ask_calls` counts HTTP request log entries, not distinct questions, and does not imply that every request succeeded. Complete requests and answers are in `interaction.jsonl`. Evaluation `elapsed_seconds` separately measures the shared evaluator execution time.

### Clarification diagnostics and timing

- The MCP adapter writes HTTP request start/completion and duration to `workspace/mcp_stderr.log`.
- The simulator writes request receipt, simulator start, provider attempts, completion, and error types to `logs/server.log`. Progress messages appear before the answer is ready.
- `logs/interaction.jsonl` retains one completed record per logged request, including `time` (the existing start timestamp), `started_at`, `finished_at`, and monotonic `elapsed_seconds`. Failed simulator calls are timed too. A missing completed record does not prove that the request never arrived.

Provider retries and JSON repair share a 140-second deadline; connect/read timeouts and retry sleeps use the remaining budget. Synchronous HTTP reads are not a strict wall-clock deadline if a provider keeps sending bytes. The MCP adapter separately bounds its HTTP await at 160 seconds, with a 5-second connect timeout and a 150-second read timeout. This leaves time to report an error before the existing 180-second MCP tool timeout. The adapter does not automatically resend questions.

The original generation `elapsed_seconds` includes clarification waits. `interaction.simulator_elapsed_seconds` sums the simulator's server-side time from receiving each `/session/ask` request until producing its response. It includes prompt construction, the LLM provider request, retries, and response parsing, but excludes client-side MCP adapter and network time before the request reaches the simulator or after the response leaves it; it is therefore neither pure model inference time nor the complete MCP round-trip time. Because this server-side measure has a clear and reproducible boundary, PrepBench currently uses it as the operational clarification-time measure. For completed runs with valid request durations, `elapsed_seconds_excluding_simulator` subtracts this measure from the original elapsed time. Both `detail/generation.json` and `result.json` retain the adjusted value and its scope. Missing durations are not silently replaced by zero; failed or interrupted runs do not receive an adjusted value. Concurrent work or overlapping requests require interval accounting before interpreting this subtraction as active agent time.

## Simulator and isolation

The simulator uses the model and API configured in the host-side `PrepBench/.env`; use `.env.example` as a template. Local credentials are not included when sharing the project. Process environment variables take precedence. Round and question budgets follow the interact protocol above. For reproducible experiments, fix the simulator model, temperature, and related environment settings.

- `direct` mounts `query.md` read-only at `/workspace/query.md`, starts no simulator, and provides no clarification tool.
- `clarified` mounts `query_full.md` read-only at `/workspace/query.md` and starts no simulator.
- `interact` mounts `query.md` at the same path and starts a host-side FastAPI simulator. The agent asks questions within the same session through the MCP adapter, which forwards them over HTTP; each question does not require resuming the agent.
- Inputs are mounted read-only at `/workspace/inputs`; the run workspace is writable at `/workspace/work`. The entire case directory is not mounted. Ground truth, evaluation configuration, the knowledge base, and the reference solution are hidden from the agent.
- Codex uses an isolated temporary configuration directory containing only the model/provider settings, reasoning effort, and authentication. Host session history, MCP configuration, and skills are not imported. Only the current session is archived; credentials are not archived.
- `command.json` stores the actual Docker arguments for diagnostics. Temporary directories and ports expire after the run, so it should not be treated as a directly replayable script.
- Runs use independent workspaces. Cleanup of the container and simulator is attempted after normal completion, errors, and timeouts. Do not modify assets while they are mounted as inputs.

Historical exploratory runs, case_173/242, and per-item diffs remain in `PandasLift/benchmark/PrepBench`. Some reference programs use legacy relative paths in `main`; when running a reference, invoke `solve` explicitly with the inputs directory for the case. These reference programs are not executed during agent generation.

## Tests

```bash
.venv/bin/python -m unittest discover -s PrepBench/scripts/tests -v
.venv/bin/python -m unittest discover -s evaluation/tests -v
.venv/bin/python -m unittest discover -s DataAgentBench/scripts/tests -v
```

Unit and integration tests use simulated agents and simulator responses. They cover the pipeline for interact and clarified modes, skipping evaluation after generation failure, preserving generation records during re-evaluation, timing, and result aggregation. Real-model runs are stored under their respective `runs` directories; simulated tests are not evidence of real-model correctness.

## OpenCode options

Both `generate.py` and `run_benchmark.py` support `--agent codex|opencode`, with `codex` as the default. See [runners/README.md](../runners/README.md) for OpenCode configuration isolation, token accounting, and image setup. The following example uses a custom provider; prepare the local configuration according to the shared instructions first:

```bash
.venv/bin/python PrepBench/scripts/run_benchmark.py \
  --case 001 --mode clarified --backend pandas \
  --agent opencode --opencode-config runners/configs/opencode/opencode.json \
  --model custom/gpt-6-astra --image dfarena-agent-sandbox:latest
```

OpenCode interact support has not yet been validated with a real model; the recorded OpenCode validation used `clarified` mode. OpenCode saves `logs/agent_events.jsonl`, `logs/agent_stderr.log`, and `detail/agent_exec_timing.json`. The session ID is recorded in `generation.json`, and the session database is archived at `detail/opencode_sessions/opencode.db`. Stage-file and `result.json` paths are unchanged.
