# DataAgentBench runner

Run commands from the dfArena root with Python 3.11+, Docker, and local agent configuration. See [shared runner configuration](../../runners/README.md#configuration). The default image is `dfarena-agent-sandbox:latest` and must contain the selected agent CLI and dataframe dependencies.

## Run a task

Prefer explicit `--agent` and `--model` arguments so the command identifies the actual agent and model:

```bash
# Codex
.venv/bin/python DataAgentBench/scripts/run_benchmark.py \
  --dataset DataAgentBench/bookreview --task task2 \
  --agent codex --model gpt-6-astra --backend pandas

# OpenCode: custom must match a provider in the OpenCode configuration.
.venv/bin/python DataAgentBench/scripts/run_benchmark.py \
  --dataset DataAgentBench/bookreview --task task2 \
  --agent opencode --model custom/gpt-6-astra --backend polars
```

Use `--image <your-local-image>` to select another image. Backends are `pandas`, `polars`, and `ibis`.

| Argument | Meaning |
|---|---|
| `--agent` | Agent implementation: `codex` (default) or `opencode`. |
| `--model` | Actual model override; otherwise read from the selected agent's configuration. OpenCode requires `provider/model`. |
| `--agent-model` | Optional output directory label only. It does not select or change the agent or model. |
| `--timeout` | Agent process timeout in seconds; default 600. |
| `--evaluation-timeout` | Evaluation timeout in seconds; default 120. |

The CLI spelling is `--agent-model`, not `--agent_model`; `agent_model` is the internal Python attribute. Normally omit this option: the label is inferred as `codex_gpt-6-astra` or `opencode_gpt-6-astra`, without the OpenCode provider prefix. Explicit labels are sanitized for use as directory names. Reasoning effort comes from agent configuration and is recorded alongside the model.

## Pipeline

- `generate.py` prepares task inputs, runs the agent in Docker, and saves `detail/generation.json`.
- `evaluate.py` runs the task's original `validate.py` and saves `detail/evaluation.json`. Re-evaluation preserves the generation record.
- `run_benchmark.py` chains both stages and updates `result.json`. Generation failure skips evaluation; the command exits with 0 only when evaluation passes.

The summary can be rebuilt with `runners.results.summarize(run_dir)`. An answer mismatch gives `passed=false`; an evaluation error or timeout gives `passed=null`.

## Run artifacts

```text
DataAgentBench/<dataset>/output/<task>/<agent-model>/<backend>/rNNN/
  result.json                       # Generation and evaluation summary
  detail/
    generation.json
    evaluation.json
    agent_exec_timing.json
    prompt.txt
    command.json
    codex_sessions/                  # Codex runs only
    opencode_sessions/opencode.db    # OpenCode runs only
  logs/
    agent_events.jsonl              # Native CLI event stream
    agent_stderr.log
    evaluation.log                   # Combined validator stdout/stderr
  solution/
    solution.py
    answer.json
  work/                              # Agent's writable workspace
```

Run numbers increment within each task/label/backend combination. Generation requires a fresh directory; `output/` is Git-ignored. The native session archive and CLI events are both retained; see [session archives](../../runners/README.md#session-archives).

## Timing and usage

Generation timing covers only the agent process inside Docker; evaluation timing separately covers the validator's Docker invocation. Token counters are extracted from agent events and normalized by the shared adapters. Definitions and coverage limitations, including auxiliary calls missing from CLI events, are documented in [Timing and token usage](../../runners/README.md#timing-and-token-usage).

## Run stages separately

Use a fresh path for generation, then pass the same path to evaluation:

```bash
DAB_RUN_DIR=DataAgentBench/bookreview/output/task2/manual/pandas/r001

.venv/bin/python DataAgentBench/scripts/generate.py \
  --dataset DataAgentBench/bookreview --task task2 \
  --agent codex --model gpt-6-astra --backend pandas \
  --run-dir "$DAB_RUN_DIR"

.venv/bin/python DataAgentBench/scripts/evaluate.py \
  --dataset DataAgentBench/bookreview --task task2 \
  --run-dir "$DAB_RUN_DIR"
```

This runner follows the repository's [isolation and validation conventions](../../README.md#isolation-and-validation). DataAgentBench uses its original task validators, rather than the shared CSV comparator.

## Tests

```bash
.venv/bin/python -m unittest discover -s DataAgentBench/scripts/tests -v
```
