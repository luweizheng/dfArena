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

The current runners record correctness checks, execution status, agent elapsed time, token usage, and session traces. These records support further analysis of repair behavior and failure causes, including ambiguous specifications, agent misunderstandings, backend semantic differences, API friction, and environment failures. Standalone solution runtime, billing cost, and automatic root-cause classification are not yet uniform evaluation metrics.

Pandas is used as a reference dataframe system, while Polars and Ibis represent alternative eager/vectorized and lazy relational execution styles. Cross-backend comparison is an important experimental dimension, but the broader focus is reliable dataframe programming by coding agents.

## Framework overview

dfArena organizes experiments around benchmark tasks, coding agents, and dataframe backends. For each run, a selected agent generates and executes code with the target backend, and the benchmark evaluator checks the resulting outputs. Each benchmark has its own directory so that task assets and benchmark-specific logic remain easy to find. To keep these workflows consistent and avoid maintaining separate copies of the same agent and reporting code, reusable functionality is extracted into shared components.

```text
runners/          Shared agent adapters, CLI options, timing, and run reports
DataAgentBench/   Task assets and benchmark-specific generation/evaluation for DataAgentBench
PrepBench/        Task assets, interactive clarification simulator, and table evaluation for PrepBench
evaluation/       Shared tabular-output evaluation protocol and code, aim to compare ground truth and candidate solutions
docker/           Agent execution image
```

Agent selection and model arguments are defined in `runners/agents/`. The adapters handle agent-specific (Codex/OpenCode) configuration, commands, session archives, and usage parsing. Report format and log conventions apply across benchmarks, while their task and workspace layouts remain benchmark-specific.

Runs execute in independent Docker containers with task-specific input mounts and a writable workspace. Host session history, skills, MCP configuration, hidden reference solutions, ground truth, and evaluator configuration are not imported into the generation container by default. Any additional skills or MCP connectivity must be supplied explicitly by the execution setup. Interactive PrepBench runs use a separate simulator with private task assets to answer clarification requests.

DataAgentBench is the complete runnable entry point in the current commits.
PrepBench and the shared table evaluator are being integrated: the PrepBench entry scripts are committed, but their supporting assets and modules are not yet fully committed.

## Quick start

Use Python 3.11+ and Docker, and run the following commands from the repository root.

First, create local configuration for the agent you want to use, starting from the [Codex example](runners/configs/codex/config.example.toml) or [OpenCode example](runners/configs/opencode/opencode.example.json). Save it as `runners/configs/codex/config.toml` or `runners/configs/opencode/opencode.json`, respectively. Set the provider endpoint, model, reasoning effort, and required credential environment variables. Local configuration files are Git-ignored. See [Configuration](runners/README.md#configuration) for overrides.

Build the sandbox image, which includes both agent CLIs and the dataframe dependencies:

```bash
docker build \
  -f docker/agent-sandbox.Dockerfile \
  -t dfarena-agent-sandbox:latest .
```

Run a DataAgentBench task with either agent:

```bash
# Codex
python DataAgentBench/scripts/run_benchmark.py \
  --dataset DataAgentBench/stockindex --task task1 \
  --agent codex --model gpt-6-astra --backend pandas

# OpenCode: custom must match a provider in your configuration.
python DataAgentBench/scripts/run_benchmark.py \
  --dataset DataAgentBench/stockindex --task task1 \
  --agent opencode --model custom/gpt-6-astra --backend pandas
```

Supported dataframe backends are `pandas`, `polars`, and `ibis` (with DuckDB). Prefer `--agent` and `--model` to select the actual agent and model; OpenCode uses `provider/model`. The optional `--agent-model` argument only overrides the output directory label. Reasoning effort comes from agent configuration.

## Execution and results

Each benchmark's `run_benchmark.py` chains generation and evaluation:

```text
run_benchmark.py
  → generate.py: prepare task inputs, execute the agent, collect outputs and records
  → evaluate.py: check generated outputs with the benchmark's evaluator
```

Generation checks that required outputs are present and records execution failures and timeouts. Failed generation skips evaluation; a normal end-to-end run exits successfully only when evaluation passes. Generation and evaluation retain independent stage reports, and `runners/results.py` combines them into `result.json`.

The shared result and log conventions are:

```text
<run_dir>/
  result.json                       # Generation/evaluation summary
  detail/
    generation.json                 # Code generation status, timing, usage, artifact paths
    evaluation.json                 # Evaluation status and correctness result
    agent_exec_timing.json           # Agent process timing, when available
    codex_sessions/                 # Native archive for Codex runs
    opencode_sessions/opencode.db   # Native archive for OpenCode runs
  logs/
    agent_events.jsonl              # Native CLI events; schema depends on the agent
    agent_stderr.log
    evaluation.log                  # Combined output when using an external validator
```

Runs retain both CLI events and native session archives when available. Generated code, answers, and workspace locations are documented by each benchmark. DataAgentBench stores runs under `DataAgentBench/<dataset>/output/<task>/<agent-model>/<backend>/rNNN/`.

Agent timing covers the agent process inside Docker, including its tool execution, and excludes Docker startup, session archiving, and evaluation. Token usage comes from CLI events and is normalized by the adapters. See the [shared runner documentation](runners/README.md) for timing scope, token accounting limitations, and session archives.

## Evaluation

Evaluation is separate from generation and checks two types of output: an answer to an analytical question, or a table produced by data processing. DataAgentBench and PrepBench currently provide tasks for these two output types, respectively.

- **Answer evaluation:** checks the generated answer against task-specific correctness criteria. For DataAgentBench, the runner reads the answer from `answer.json` and invokes the task's original `validate.py` in a separate container. The validator determines whether the answer passes; its coverage depends on the task. For example, some validators check whether expected answer text is present without rejecting extra answers.
- **Table evaluation:** compares a generated table with a ground-truth table according to an evaluation configuration. For PrepBench, the shared [`evaluation/`](evaluation/README.md) module normalizes field values, aligns rows using configured keys, and compares values using the declared types and numeric tolerances. Row order is ignored by default; when required, order checks allow tied rows to exchange positions according to the configured ordering rules.

See the [DataAgentBench runner documentation](DataAgentBench/scripts/README.md) and [PrepBench runner documentation](PrepBench/README.md) for benchmark-specific commands and evaluator details.

## Workload domain taxonomy

A workload has one primary `domain`.

| Domain | Typical subdomains | Examples |
| --- | --- | --- |
| `business` | `sales_operations`, `customer_relationship_management`, `retail_operations`, `workforce_analytics`, `site_selection`, `local_businesses`, `business_reviews` | CRM, store performance, inventory, customer, sales and local-business analysis |
| `finance` | `stock_market`, `financial_reporting`, `investment` | Stock prices, securities, trading and financial indicators |
| `software` | `package_ecosystem`, `open_source_repositories`, `cybersecurity` | Software packages, GitHub repositories and CVE data |
| `health` | `cancer_research`, `clinical`, `public_health` | Clinical and biomedical data |
| `science` | `patents`, `research_data`, `scientific_literature` | Patents and other scientific data |
| `public_sector` | `civic_data`, `government_contracts`, `procurement` | Civic documents, public funding and government awards |
| `media_culture` | `news`, `books_reviews`, `film_television`, `music` | News, books, films and music |
| `sports` | `league_statistics`, `game_results` | NBA and other sports standings or results |
| `education` | `student_records`, `learning_analytics` | Education and learning datasets |
| `geospatial` | `maps`, `locations`, `geospatial_documents` | Location and geometry-heavy datasets |

Use `finance` as a peer of `business`: business covers organizational operations, customers, sales, retail and local businesses, while finance covers markets, securities and financial measures.
