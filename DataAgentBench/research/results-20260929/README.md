# DataAgentBench complete-requirement results — 2026-09-29

17 datasets, 104 tasks per backend, 312 retained attempts. Pandas, Polars and Ibis each pass **88/104 (84.6%)**.

| Dataset | Pandas | Polars | Ibis |
|---|---:|---:|---:|
| DEPS_DEV_V1 | 2/2 | 2/2 | 2/2 |
| GITHUB_REPOS | 4/4 | 4/4 | 4/4 |
| PANCANCER_ATLAS | 3/3 | 3/3 | 3/3 |
| PATENTS | 3/3 | 3/3 | 3/3 |
| agnews | 2/4 | 2/4 | 1/4 |
| bookreview | 3/3 | 3/3 | 3/3 |
| civic_unstructured | 5/10 | 5/10 | 5/10 |
| crmarenapro | 13/13 | 13/13 | 13/13 |
| cve | 9/10 | 7/10 | 9/10 |
| googlelocal | 4/4 | 4/4 | 4/4 |
| imdb | 9/10 | 10/10 | 9/10 |
| krama | 8/10 | 8/10 | 8/10 |
| music_brainz_20k | 3/3 | 3/3 | 3/3 |
| stockindex | 3/3 | 3/3 | 3/3 |
| stockmarket | 5/5 | 5/5 | 5/5 |
| usaspending | 5/10 | 6/10 | 6/10 |
| yelp | 7/7 | 7/7 | 7/7 |

## Protocol and interpretation

- Codex, gpt-6-astra, low reasoning; agent budget 600 seconds, evaluation budget 120 seconds. Full description and enabled hints were delivered in the initial prompt. No independent solution replay was performed.
- Ordinary wrong answers and agent timeouts are retained. Confirmed infrastructure failures were discarded and retried. Each task has one retained attempt, not a best-of-N selection based on correctness.
- Polars cve/task4 and agnews/task3 timed out and remain unscored; both count in the 104-task denominator.
- Agent seconds cover the timed agent process, including exploration, code execution and repair; they are not standalone program runtime. Current upstream code includes later changes, while these experiments used the recorded frozen runner hashes and image digest.
- API-equivalent amounts are historical estimates under the recorded September 24 pricing snapshot, not subscription charges. Only retained attempts are included; two timeout costs are unavailable. Do not treat the sum as total spending.
- Results use approved task clarifications and validator revisions, and are not unmodified upstream DAB scores. CRM task8 changes the eligibility condition. CVE task2 accepts either verified tied vendor. Stockindex task3 retains the upstream two-answer-set rule; its special DCA clarification was withdrawn before the retained replacement run.
- CRM task2 retains the user-approved temporary multi-policy scoring rule; upstream intent, policy timing and hidden bundle semantics remain unresolved. This is an explicit scoring limitation, not a newly resolved task interpretation.
- CRM task1 keeps its original permissive validator by explicit decision; all three retained answers are exactly Authority. Civic task3 was rescored with the empty-result expression fix, without changing any generated answer or solution.
- Scoring passes are not proof of complete code semantics or backend compliance. Full per-task semantic review remains unfinished. USAspending qualitative amount descriptions still require interpretation; no private exact-amount table was supplied.

## Contents and data availability

`results.json` contains portable metrics, answers, artifact hashes, prompt delivery and validator provenance. `results.csv` is a flat overview. `pricing_snapshot.json` preserves the historical fee assumptions; this export does not assert that those prices are current. Revision labels identify historical local audit records without exposing host paths. `repair_rounds_observed` is a partial passive observation, not a complete count of semantic repairs. `artifacts/` contains retained solutions, answers when present, and exact initial prompts. `inputs/` contains frozen context/task text plus data-file hashes; `runners/` records configurations and frozen implementation hashes. `validators/` preserves the exact scoring code bytes; repository text files may otherwise have platform-specific line endings. The local `.gitattributes` disables newline conversion only within this archived result bundle, so its checksums remain portable.

Large Parquet data, native sessions, raw logs, local account configuration and transient work files are not included in this curated export. Existing `.gitignore` rules remain in force. Newly adapted dataset data remain local; metadata records source provenance, paths, sizes and hashes. A fresh clone needs those data files provisioned separately before rerunning all datasets. This export is intended for review; it is not a self-contained data release. Some generated solutions depend on intermediate files produced during the original agent session (for example, qualitative_review.json or classified.pkl); standalone replayability is not guaranteed, and those workspace files are not included.

Historical review notes may contain paths to local evidence archives; the metrics and artifacts in this directory use relative paths. No generation was rerun to create this export.

The original upstream benchmark is [DataAgentBench](https://github.com/ucbepic/DataAgentBench). Data access and redistribution must follow its applicable terms.
