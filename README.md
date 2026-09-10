# dfArena

`dfArena` is a benchmark and evaluation framework for coding agents that solve realistic tabular data-analysis tasks with dataframe systems.

## Framing

> How reliably can coding agents solve realistic, executable tabular data-analysis tasks using dataframe systems, and how do workload, natural-language intent, model, harness, and backend characteristics affect correctness, efficiency, and cost?

Pandas is one of the most widely used tools for tabular data analysis and processing.
However, its single-machine, in-memory execution model limits scalability.
To address these challenges, the data community has developed alternative interfaces and execution systems, including Polars, PySpark, and Ibis, which have attracted interest from users. Migrating existing Pandas workflows to these systems nevertheless requires understanding differences in APIs and execution semantics while preserving results.

With the development of AI coding agents, data analysis and processing are expanding from humans writing programs by hand to humans describing their requirements in natural language and agents exploring data, generating programs, and executing them.
Agents can therefore help migrate existing Pandas code or implement natural-language requirements directly using different backends.
When a natural-language description is clear and complete, an agent can proceed directly to implementation. In many cases, however, users' initial descriptions are vague or incomplete, and users progressively clarify their intent and supplement their requirements through interaction with the agent.

**dfArena aims to systematically evaluate the correctness and reliability of AI-assisted DataFrame programming across three practical scenarios:**

1. **Code-to-Code Transpilation:** Translate existing Pandas programs to other backends, enabling potential acceleration or execution at larger scales while preserving program semantics.
2. **Direct NL-to-DataFrame:** Generate and execute programs for a target backend from clear natural-language requirements to produce correct analytical answers or data-processing results.
3. **Interactive NL-to-DataFrame:** Address incomplete or ambiguous requirements through interaction that progressively clarifies user intent and supplies missing requirements, then generate and execute programs.

Through experiments across tasks, models, and backends, dfArena examines agents' capabilities and limitations, error types, and execution behavior in these scenarios. Its central concern is **whether requirements are correctly understood and whether those requirements are faithfully implemented across different backends**.

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
