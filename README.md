# dfArena

`dfArena` is a benchmark and evaluation framework for coding agents that solve realistic tabular data-analysis tasks with dataframe systems.

## Framing

The goal is not simply to compare dataframe APIs or produce a backend leaderboard. The central question is:

> How reliably can coding agents solve realistic, executable tabular data-analysis tasks using dataframe systems, and how do workload, natural-language intent, model, harness, and backend characteristics affect correctness, efficiency, and cost?

The full evaluation object is:

```text
Task / NL intent
    x Agent / Model
    x Dataframe backend
```

The benchmark measures more than whether generated code runs. It can evaluate answer correctness, execution validity, repair behavior, agent time, solution runtime, token usage, and cost. The framework also separates different sources of failure, such as ambiguous specifications, agent misunderstandings, backend semantic differences, API friction, and environment failures.

Pandas is used as a reference dataframe system, while Polars and Ibis represent alternative eager/vectorized and lazy relational execution styles. Cross-backend comparison is an important experimental dimension, but the broader focus is reliable dataframe programming by coding agents.

## Quick start

Build the agent sandbox from the repository root:

```bash
docker build \
  -f docker/agent-sandbox.Dockerfile \
  -t dfarena-agent-sandbox:latest .
```

Run a task:

```bash
python DataAgentBench/scripts/run_benchmark.py \
  --dataset DataAgentBench/stockindex \
  --task task1 \
  --agent-model codex_gpt-6 \
  --backend pandas
```

Supported dataframe backends currently include `pandas`, `polars`, and `ibis`.
