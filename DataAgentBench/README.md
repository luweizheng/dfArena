# DataAgentBench

A dataframe-native adaptation of [DataAgentBench](https://github.com/ucbepic/DataAgentBench) dataset. 

## Structure

The original DataAgentBench is for database data agent, here we are a dataframe benchmark, we need to remove database-related stuff and turn it into a dataframe-native benchmark. Each task is a tuple: (data, context, task, answer). 

- `metadata.yaml`: dataset characteristics for research analysis and paper statistics, plus file identity and navigation. Field purposes and counting conventions are defined below.
- `context/description.md`: FROM `db_description.txt`, input file paths, table schemas, field descriptions, and dataset relationships.
- `context/hints.md`: FROM `db_description_withhint.txt`, optional domain and calculation guidance.
- `data/<db_name>/<table>.parquet`: FROM `query_dataset`, convert them into parquet file which is widely used for data analysis, input tables, with no `_database` suffix.
- `tasks/task{1,2,3}/task.json`: FROM `queryN`, task IDs and natural-language queries.
- `tasks/task{1,2,3}/answer/`: FROM `queryN`, hidden ground truths and validators.
- `output/<task>/<agent-model>/<backend>/rNNN/`: isolated generation and evaluation outputs.

## Metadata for dataset analysis

Metadata describes the adapted dataset, not the machinery used to migrate it. Use a consistent set of fields across datasets:

This file is for researcher-side analysis and paper statistics. It is not an agent input, is not mounted into the solution-generation container, and is not required by task JSON. Agent-facing file paths, schemas, and representation guidance belong in `context/description.md`; approved task clarifications belong in `context/hints.md`.

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

Original database file lists, migration tool versions, BSON source paths, old SQL identifier spellings, SQLite declarations/storage counters, and empty source constraints are omitted. Useful conversion consequences belong in concise `source.adaptations` entries; field-reading guidance and approved task clarifications remain in `context`. Conversion notes refer to the initial adaptation unless explicitly marked as subsequent revisions. Dated migration and experiment audit records under `research/` remain historical records and are not rewritten by metadata cleanup.

## Execution boundary

During solution generation, the runner must expose only input data, the context, and the current task JSON. Keep researcher-side metadata outside the agent sandbox. Do not mount the whole dataset directory into agent sandbox: the whole dataset directory contains answers and historical runs. Keep solution outputs in an isolated run workspace.

After generation ends, freeze the solution and evaluate it in a separate process/container that can read `answer/`. Never mount answers into a still-running agent session.

## Evaluation status

Except for explicitly approved task revisions recorded below, this reorganization preserves the existing queries, ground truths, and validators without strengthening their correctness checks.

## Complete-requirement experiments

For the complete-requirement row, including S0 without an extra skill, pass
`--complete-requirements` to `scripts/run_benchmark.py`, the top-level entry point
that runs generation followed by evaluation. It forwards the flag to
`scripts/generate.py` (which also accepts it when run independently). This explicitly enables hints
and includes the full UTF-8 contents of both `context/description.md` and
`context/hints.md` in the agent's initial prompt. Both documents have equal status
as task requirements; approved task-specific clarifications belong in the hints
of the isolated task input. This does not add a skill or a code replay stage.

Missing, empty, or undecodable documents stop preparation before agent execution.
The exact prompt is saved to `detail/prompt.txt`; `detail/input_delivery.json`
records the delivery mode, hints state, source hashes, and prompt hash. Delivery
does not itself prove that the generated code follows every requirement, and an
answer-only validator may not check those rules.

Without the flag, the prior file-reference prompt is retained for compatibility;
it is not a verified complete-requirement condition or an isolated no-hints condition.

## Approved task revisions

### 2026-09-25: crmarenapro task8 — positive outgoing-transfer eligibility

- Scope: a user-approved task specification revision, not a claim about the original DAB authors' intended interpretation. This is a revised local task and must not be reported as an unmodified DAB result.
- File: `crmarenapro/tasks/task8/task.json`, `query`; only the eligibility clause in the opening sentence changes.
- Original clause: `among those who handled more than 0 cases.`
- Revised clause: `among those who handled more than 0 cases and had at least one outgoing transfer during that period.`
- Reason: the original question admits agents with zero outgoing transfers, while its fixed reference answer identifies an agent with one outgoing transfer. The revision explicitly restricts the comparison to positive outgoing-transfer counts.
- Existing transfer definitions remain in the question. No closed-case restriction is added, and the handled-case threshold remains greater than zero. The rule is not duplicated in shared hints.
- Ground truth and validator are retained. Data inspection found one eligible agent, with one outgoing transfer, under both checked interpretations of the four-quarter window: 2022-04-10 through 2023-04-10 and 2022-04-01 through 2023-03-31. The change therefore reduces the candidate set to a single agent; these checks do not settle the original author's time-window convention.
- This changes the task text for any run that loads this task JSON, including runs without the complete-requirements flag. Future paired experiments must use the same recorded task revision on both sides.
- Provenance: [original question](https://github.com/ucbepic/DataAgentBench/blob/main/query_crmarenapro/query8/query.json), [original answer](https://github.com/ucbepic/DataAgentBench/blob/main/query_crmarenapro/query8/ground_truth.csv), and [original validator](https://github.com/ucbepic/DataAgentBench/blob/main/query_crmarenapro/query8/validate.py). The three upstream files were checked against the local source on 2026-09-25.

### 2026-09-25: crmarenapro task9 — mean case closure time

- User-approved clarification in shared `crmarenapro/context/hints.md`: compare states by the arithmetic mean closure time of closed cases, weighting each case equally; duration is closed date/time minus created date/time.
- This resolves the mean/median/fastest-case ambiguity. It does not add a state-field mapping, date-window convention, minimum sample count, or reference answer to the hints.
- The task query, ground truth, validator, and generation code are retained. The clarification is included in the existing complete-requirements prompt; no model experiment was run for this edit.

### 2026-09-25: crmarenapro task10 — open cases count toward eligibility

- User-approved clarification in shared `crmarenapro/context/hints.md`: when determining eligibility for having handled more than one case, include cases that have not yet been closed.
- Only this eligibility clarification is added. The task query, ground truth, validator, and generation code are retained. The existing complete-requirements prompt was checked to include the added hint; no model experiment was run for this edit.

### 2026-09-25: crmarenapro task12 — April cohort by company signing date

- User-approved clarification in shared `crmarenapro/context/hints.md`: for the April 2023 average sales-cycle comparison, select opportunities by the corresponding contract company signed date, not the opportunity creation date or its own close date.
- The hint explicitly identifies this comparison; no additional ownership or weighting rule is added. Task text, ground truth, validator, and generation code are retained. The existing complete-requirements prompt was checked to include this hint; no model experiment was run for this edit.

### 2026-09-25: crmarenapro task13 — correct order amount definition

- User-approved correction in `crmarenapro/tasks/task13/task.json`, `query`: replace `The sales amount for an order is calculated as the product of the quantity and the unit price from the Order object (Quantity * UnitPrice).` with `The sales amount for an order is the sum of Quantity * UnitPrice across all of its order line items (OrderItem).`. Quantity and UnitPrice belong to OrderItem, and an order may contain multiple line items.
- Only this definition is changed. Contract-signing eligibility and all other task text are retained; shared hints, ground truth, validator, and generation code are unchanged. Order-to-contract mapping and sales attribution remain under review; this correction does not make the entire task fully clarified.
- Both existing prompt modes were checked to include the corrected definition. No model experiment was run. Record this local task revision in results and use the same corrected task text across paired experiment conditions.

### 2026-09-25: crmarenapro task13 — attribute order sales to the order owner

- User-approved clarification in shared `crmarenapro/context/hints.md`: when comparing agents' order sales amounts, attribute each order's sales amount to that order's owner.
- Only the attribution rule is added; no time-window or order-to-contract matching rule is added. Matching remains a reasoning task using the supplied data, not a confirmed ambiguity requiring a new hint. Conditional owner comparisons support this choice but do not establish the original author's full matching logic.
- This resolves the sales-attribution review noted in the preceding correction entry. Existing task text, answers, validators, and generation code are retained. The complete-requirements prompt was checked to include the new hint once; no model experiment was run.

### 2026-09-25: stockmarket task4 — rank by excess up days

- User-approved clarification in shared `stockmarket/context/hints.md`: when selecting the top five stocks with more up days than down days in 2017, rank by up-day count minus down-day count, descending.
- Existing eligibility and up/down definitions are retained; no tie-break rule or reference company names are added. Data checks found no tie at the fifth-place boundary under this metric. Task text, answers, validators, and generation code are unchanged. The existing complete-requirements prompt was checked to include the new hint once; no model experiment was run.

### 2026-09-25: yelp task1 — average Indianapolis ratings by review

- User-approved clarification in shared `yelp/context/hints.md`: pool all reviews of businesses in Indianapolis, Indiana, and take the arithmetic mean of their ratings, weighting each review equally. The scope is this city-average question; other rating questions are reviewed separately.
- The 8 selected businesses have 117 reviews. The pooled review mean matches the reference, while averaging business means differs; neither the reference value nor business identifiers are added to hints. Task text, answers, validators, and generation code are unchanged. The existing complete-requirements prompt was checked to contain the hint once; no model experiment was run.

### 2026-09-25: yelp task2 — count actual reviews by state

- User-approved clarification in shared `yelp/context/hints.md`: compare U.S. state review counts using actual review-table records linked to businesses in each state, not sums of business.review_count. Only the count-source rule is added; the task2 average-rating weighting remains under review.
- The discrepancy exists in the supplied source snapshot: original DuckDB review records and the relevant original BSON business fields match the current Parquet data. The source documentation does not establish why those counts differ. Task text, answers, validators, and generation code are unchanged. The existing complete-requirements prompt was checked to contain the hint once; no model experiment was run.

### 2026-09-25: yelp task2 — average the selected state ratings by review

- User-approved clarification in shared `yelp/context/hints.md`: for the U.S. state with the most reviews, pool all reviews of businesses in that state and take the arithmetic mean of their ratings, weighting each review equally. This resolves the weighting review noted in the preceding task2 entry.
- This addition concerns only the selected-state average; the approved count-source rule and all previous hints are retained. Task text, answers, validators, and generation code are unchanged. The existing complete-requirements prompt was checked to contain the new hint once and retain the previous hints; no model experiment was run.

### 2026-09-25: yelp task4 — restrict the rating population to credit-card businesses

- User-approved clarification in shared `yelp/context/hints.md`: calculate the selected category average using only businesses in that category that accept credit card payments.
- Only the rating population is clarified; task4 weighting and category interpretation are not changed by this addition. Existing hints, task text, answers, validators, and generation code are retained. The existing complete-requirements prompt was checked to contain the hint once; no model experiment was run.

### 2026-09-25: yelp task4 — combine rating scope and equal review weighting

- User approved pooling all reviews of credit-card-accepting businesses in the selected category and taking the arithmetic mean, weighting each review equally. The earlier scope-only hint is replaced by one combined rule; all other hints are retained.
- This resolves the task4 weighting review in the preceding entry. No category mapping, task text, answer, validator, or generation code is changed. The existing complete-requirements prompt was checked to contain the combined rule once; no model experiment was run.

### 2026-09-25: yelp — consolidate the average-rating rule

- User approved one dataset-wide rule: take the arithmetic mean of review ratings satisfying the current task filters, weighting each review equally. Business scope, time period, and other task filters apply before averaging.
- This supersedes the separate task1 and task2 rating hints and the weighting portion of the task4 hint. The actual-review count source for state comparisons and the task4 credit-card-only business scope remain as independent hints. The general rule also covers the rating calculations in tasks 5 and 6; other task requirements remain unchanged.
- Existing complete-requirements prompts for tasks 1, 2, 4, 5, and 6 were checked to contain the general rule once, preserve the two independent rules and each task query, and omit the superseded text. Task files, answers, validators, description, and generation code are unchanged. No model experiment was run.


### 2026-09-25: yelp task6 — apply the minimum-review threshold within the rating period

- User-approved clarification in shared `yelp/context/hints.md`: the requirement of at least five reviews applies to actual reviews received during January 1 through June 30, 2016. It does not use lifetime review counts to determine eligibility for this half-year comparison.
- Existing hints are retained. Task text, answers, validators, description, and generation code are unchanged. The existing complete-requirements prompt was checked to contain the new hint once; no model experiment was run.


### 2026-09-25: yelp task7 — count reviews in each applicable business category

- User-approved clarification in shared `yelp/context/hints.md`: for reviews since 2016 by users registered in 2016, a business may belong to multiple categories listed in its description; each review counts once in each applicable category. This clarification is scoped to this category-ranking question.
- All existing hints are retained. Task text, answers, validators, description, and generation code are unchanged. The existing complete-requirements prompt was checked to include the new hint once and retain the task query and previous hints. No model experiment was run.


### 2026-09-25: PANCANCER_ATLAS task1 — group LGG expression by ICD-O-3 histology code

- User-approved clarification in shared `PANCANCER_ATLAS/context/hints.md`: for the LGG IGF2 average-expression task, group patients by `clinical_info.icd_o_3_histology`. This resolves the choice between the histology-name field and ICD-O-3 codes; it is scoped to this task.
- The existing expression transformation and eligibility rules are retained. Task text, answers, validators, description, and generation code are unchanged. The existing complete-requirements prompt was checked to contain the new hint once, retain the previous hints, and preserve the task query. No model experiment was run.


### 2026-09-25: PANCANCER_ATLAS task2 — group BRCA mutation percentages by histological type name

- User-approved clarification in shared `PANCANCER_ATLAS/context/hints.md`: for the comparison of CDH1 mutation percentages among living BRCA patients, group by `clinical_info.histological_type`. The preceding LGG IGF2 task remains scoped to `clinical_info.icd_o_3_histology`.
- This addition specifies the grouping field. Existing hints, task text, answers, validators, description, and generation code are retained. The existing complete-requirements prompt was checked to contain the new hint once and preserve the previous hints and task query. No model experiment was run.


### 2026-09-25: PANCANCER_ATLAS task3 — group the female BRCA chi-square analysis by histological type name

- User-approved clarification in shared `PANCANCER_ATLAS/context/hints.md`: for the chi-square association between histological types and CDH1 mutation presence among female BRCA patients, group by `clinical_info.histological_type`. The rule is scoped to this analysis and does not add an alive-only restriction.
- Existing hints, task text, answers, validators, description, and generation code are retained. The existing complete-requirements prompt was checked to include the new hint once, preserve previous hints, and retain the task query. No model experiment was run.


## Reviewed experiment snapshot (2026-09-29)

The [curated result bundle](research/results-20260929/README.md) reports all 17 datasets and 104 tasks on Pandas, Polars and Ibis, with 312 retained attempts. It includes exact retained prompts, generated solutions/answers, timing, token usage, historical API-equivalent estimates, and input/scoring hashes. Each backend passes 88/104 under the documented local task and scoring revisions.

Newly adapted large Parquet files are not included in this Git publication; the existing ignore policy has not been changed. Data paths, source provenance, measured sizes and hashes remain in each dataset metadata file. Populate the local data separately before running those datasets. Historical review notes and drafts retain their original dates; use the linked snapshot for current results and limitations.
