# Agent Guide

This repository studies the correctness and reliability of coding agents that generate and execute DataFrame programs from natural-language requests. It currently includes DataAgentBench and PrepBench; other challenging benchmarks may be added later. Read the root `README.md` for the implemented framework. `RESEARCH_NOTES.md` contains research ideas and hypotheses, which should not be mistaken for implemented features.

## Where to Look

- `DataAgentBench/`: Dataset-level `description.md`, optional `hints.md`, Parquet inputs, and `tasks/taskN/`. Each task's `ground_truth.csv` and `validate.py` are private evaluation assets. See `DataAgentBench/README.md` and `DataAgentBench/scripts/README.md` for execution details.
- `PrepBench/`: Each `case_XXX/` contains CSV inputs, the original `query.md`, complete `query_full.md`, clarification knowledge base `amb_kb.json`, a reference solution, and `evaluation/`. See `PrepBench/README.md` for execution and task contracts. `PrepBench/curation/` contains curation records, not runtime dependencies.
- `runners/`: Shared Codex/OpenCode adapters, timing, stage records, and `result.json` aggregation. Start here for agent or common reporting changes, and check callers in both benchmarks.
- Root `evaluation/`: Shared CSV table comparator. Consult `evaluation/README.md` and the code for types, tolerances, key alignment, ordering, and error codes. DataAgentBench currently uses task-specific `validate.py` scripts instead.
- `docker/`: Isolated execution image and in-container dependencies. The root `requirements.txt` lists host-side dependencies.

## Change Guidelines

- Keep researcher-side curation and evaluation separate from the tested agent's solving environment. During generation, expose only the query, documentation, and input data allowed for the current task. Do not mount ground truth, reference solutions, validators, evaluation configs, private clarification materials, or an entire case or dataset directory into the agent container. Evaluate separately after generation ends.
- Preserve the meaning of `direct`, `clarified`, and `interact`: the first uses the initial request, `clarified` provides the complete clarification up front, and `interact` obtains clarification incrementally from a simulated user. The two benchmarks use different clarification assets; read the relevant README before changing them.
- When changing a query, input, ground truth, validator, or evaluation config, check that they remain consistent. An existing answer passing validation does not by itself establish that the task contract is correct. Record asset or rule changes that affect experimental comparability.
- Do not equate successful generation with a correct result. Use the separate generation/evaluation stage records and final `result.json`. For comparative experiments, hold the task, model, backend, mode, image, and relevant simulator settings fixed.
- Put assets and benchmark-specific entry points for a new benchmark in its own directory. Reuse the agent and reporting mechanisms in `runners/`, and prefer the shared `evaluation/` module for table outputs. Do not hard-code benchmark-specific task rules in shared modules.
- Preserve existing uncommitted or untracked research assets and run artifacts. Do not commit `output/`, `runs/`, local agent configs, or secrets; do not put credentials in logs or documentation.

## Verification

Run commands from the repository root. Prefer the existing `.venv/bin/python`; if the environment is absent, follow `PrepBench/README.md` to install host-side dependencies. Select tests according to the scope of the change:

```bash
.venv/bin/python -m unittest discover -s runners/tests -v
.venv/bin/python -m unittest discover -s DataAgentBench/scripts/tests -v
.venv/bin/python -m unittest discover -s PrepBench/scripts/tests -v
.venv/bin/python -m unittest discover -s evaluation/tests -v
```

End-to-end runs with a real agent also require the Docker image, relevant CLI, configuration, and credentials. Passing unit tests does not verify model execution or task correctness. See each benchmark's README for commands and result directories.
