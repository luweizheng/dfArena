# DataAgentBench

A dataframe-native adaptation of [DataAgentBench](https://github.com/ucbepic/DataAgentBench) dataset. 

## Structure

The original DataAgentBench is for database data agent, here we are a dataframe benchmark, we need to remove database-related stuff and turn it into a dataframe-native benchmark. Each task is a tuple: (data, task, answer), with dataset-level documentation in description.md and hints.md.

- `metadata.yaml`: dataset characteristics for research analysis and paper statistics, plus file identity and navigation. Field purposes and counting conventions are defined below.
- `description.md`: FROM `db_description.txt`, input file paths, table schemas, field descriptions, and dataset relationships.
- `hints.md`: FROM `db_description_withhint.txt`, optional domain and calculation guidance.
- `data/<db_name>/<table>.parquet`: FROM `query_dataset`, convert them into parquet file which is widely used for data analysis, input tables, with no `_database` suffix.
- `tasks/task{1,2,3}/query.md`: FROM `queryN`, task-specific natural-language requests.
- `tasks/task{1,2,3}/ground_truth.csv` and `validate.py`: hidden answers and validators.
- `output/<task>/<agent-model>/<backend>/rNNN/`: isolated generation and evaluation outputs.

## Metadata for dataset analysis

Metadata describes the adapted dataset, not the machinery used to migrate it. Use a consistent set of fields across datasets:

This file is for researcher-side analysis and paper statistics. It is not an agent input, is not mounted into the solution-generation container, and is not required by task files. Agent-facing file paths, schemas, and representation guidance belong in `description.md`; approved task clarifications belong in `hints.md`.

| Fields | Purpose |
|---|---|
| `dataset_id`, `version`, `domain` | Identify the dataset and its primary subject area. Use one `domain` from the [workload domain taxonomy](../README.md#workload-domain-taxonomy). |
| `format`, `table_count`, `data_size_bytes` | Describe the storage format, number of physical input tables, and total on-disk Parquet size. |
| `tables[].name`, `path` | Identify and locate each table. Use the dataset-relative path to distinguish tables with the same name in different groups. |
| `tables[].rows`, `columns`, `size_bytes`, `schema` | Analyze table sizes and column types; schema records the actual Parquet/Arrow field names and types. |
| `tables[].sha256` | Verify that comparisons use the same data files; this is a reproducibility check, not a dataset complexity metric. |
| `source.benchmark`, `source.dataset`, `source.adaptations` | Record origin and concise, relevant data-conversion choices, such as JSON text or binary geometry encodings. |
| `tasks`, `context` | Record task count and IDs, and locate the task descriptions and optional hints. |

Dataset metadata does not include a `subdomain` field. The taxonomy's typical subdomains are examples, not required metadata fields. `krama` uses `geospatial` as its primary domain based on its geospatial and environmental tables; its document collection also includes health and science topics.

`table_count` equals the number of entries in `tables`; `data_size_bytes` is the sum of their `size_bytes`, not an estimate of in-memory size. Counts describe individual physical Parquet tables: for example, stockmarket contains many separate stock price tables. Compute cross-dataset averages, medians, and distributions from these basic measurements instead of duplicating derived statistics in every metadata file. The existing version label alone does not identify exact file contents; use hashes for that purpose.


## Execution boundary

During solution generation, the runner must expose only input data, selected documentation, and the current task query. Keep researcher-side metadata outside the agent sandbox. Do not mount the whole dataset directory into agent sandbox: the whole dataset directory contains answers and historical runs. Keep solution outputs in an isolated run workspace.

After generation ends, freeze the solution and evaluate it in a separate process/container that can read the selected task directory. Never mount answers into a still-running agent session.

## Evaluation status

Except for explicitly approved task revisions recorded in [curation/APPROVED_TASK_REVISIONS.md](curation/APPROVED_TASK_REVISIONS.md), this reorganization preserves the existing queries, ground truths, and validators without strengthening their correctness checks.

## Experimental modes

`scripts/run_benchmark.py` accepts `--mode direct|clarified|interact` and forwards the selected mode to `scripts/generate.py`.

- `direct`: The agent receives the task query from `tasks/<task>/query.md` and `description.md`. It does not receive `hints.md`, cannot request clarification.
- `clarified`: The agent receives the same task and data as `direct`, plus the full contents of `hints.md` in the initial prompt. This is the reference condition with manually curated guidance provided upfront.
- `interact`: The agent initially receives the same inputs as `direct`, but can ask the simulated user questions while solving the task. The host-side simulator reads the task query, description, and hidden hints to answer them.

`clarified` and `interact` use the same underlying clarification material: the former provides `hints.md` upfront, while the latter lets the agent obtain relevant answers through limited interaction. All three modes use the same inputs, task, hidden answer, validator, and evaluation protocol.

An `interact` run follows this call chain:

```text
agent reads query.md, description.md, and table inputs
  → identifies uncertainty and calls MCP clarification.ask([question, ...])
  → the simulator uses the task, description, and hidden hints to answer
  → the agent writes and executes DataFrame code
  → the evaluator compares answer.json with the task validator
```

The simulator is a separate LLM-backed service. It does not read `metadata.yaml`, ground truth, validators, or a reference solution. Provider/API failures, connection failures, and timeouts are recorded as simulator errors and cause `/session/ask` to return HTTP 502. Invalid JSON or an invalid answer contract is retried once with validation feedback; a second invalid response becomes a refusal for the affected questions. Simulator answers are not correctness labels.

Each interact session allows at most 3 successfully processed rounds, at most 10 questions per request, and at most 25 questions in total. The budget is fixed for DataAgentBench because it does not use PrepBench's ambiguity library. Complete requests and responses are stored in `logs/interaction.jsonl`; the agent receives only the public answers.

Missing, empty, or undecodable documents stop preparation before agent execution.
The exact prompt is saved to `detail/prompt.txt`; `detail/generation.json` records the selected mode, agent-visible inputs, and simulator background files. Delivery does not itself prove that the generated code follows every requirement, and an answer-only validator may not check those rules.
