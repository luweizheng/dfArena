# DataAgentBench

A dataframe-native adaptation of [DataAgentBench](https://github.com/ucbepic/DataAgentBench) dataset. 

## Structure

The original DataAgentBench is for database data agent, here we are a dataframe benchmark, we need to remove database-related stuff and turn it into a dataframe-native benchmark. Each task is a tuple: (data, context, task, answer). 

- `metadata.yaml`: NEWLY ADDED, for analysis, source provenance, table paths, measured sizes, row/column counts, SHA-256 checksums, and context references.
- `context/description.md`: FROM `db_description.txt`, table schemas, field descriptions, and dataset relationships.
- `context/hints.md`: FROM `db_description_withhint.txt`, optional domain and calculation guidance.
- `data/<db_name>/<table>.parquet`: FROM `query_dataset`, convert them into parquet file which is widely used for data analysis, input tables, with no `_database` suffix.
- `tasks/task{1,2,3}/task.json`: FROM `queryN`, task IDs and natural-language queries.
- `tasks/task{1,2,3}/answer/`: FROM `queryN`, hidden ground truths and validators.
- `output/<task>/<agent-model>/<backend>/rNNN/`: isolated generation and evaluation outputs.

## Execution boundary

During solution generation, the runner must expose only input data, the context, metadata, and the current task JSON. Do not mount the whole dataset directory into agent sandbox: the whole dataset directory contains answers and historical runs. Keep solution outputs in an isolated run workspace.

After generation ends, freeze the solution and evaluate it in a separate process/container that can read `answer/`. Never mount answers into a still-running agent session.

## Evaluation status

This reorganization preserves the existing queries, ground truths, and validators without strengthening their correctness checks.
