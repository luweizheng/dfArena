# PATENTS

The two original data groups are available as local Parquet tables.  

Original group names are retained below for interpreting the original hints. File paths are relative to the dataset root.

## publication_database

This database is stored in Parquet format and contains natural-language metadata for published patents. Each record corresponds to a single patent publication, with descriptive fields for publication details, dates, classification codes, relationships, and citations.

### publicationinfo

File: `data/publication/publicationinfo.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `Patents_info` | string | Natural-language summary of the patent publication, including key identifiers and status like publication number, application number etc,. |
| `kind_code` | string | Description of the publication kind code (e.g., type of document issued). |
| `application_kind` | string | Type of application (e.g., “utility patent application”). |
| `pct_number` | string | Patent Cooperation Treaty application number, if applicable. |
| `family_id` | int64 | Identifier linking related patents in the same family. |
| `title_localized` | string | Patent title in localized language form. |
| `abstract_localized` | string | Patent abstract in natural language. |
| `claims_localized_html` | string | Claims section in HTML format containing readable text. |
| `description_localized_html` | string | Description section in HTML format containing readable text. |
| `publication_date` | string | Publication date in natural language format (e.g., “March 15th, 2020”). |
| `filing_date` | string | Filing date in natural language format. |
| `grant_date` | string | Grant date in in natural language format. |
| `priority_date` | string | Priority date in in natural language format. |
| `priority_claim` | string | List of claimed priority applications. |
| `inventor_harmonized` | string | Harmonized list of inventors. |
| `examiner` | string | Examiner(s) handling the case. |
| `uspc` | string | United States Patent Classification code(s). |
| `ipc` | string | International Patent Classification code(s). |
| `cpc` | string | JSON-like list of Cooperative Patent Classification entries, each with code and metadata. |
| `citation` | string | List of cited patents and non-patent literature. |
| `parent` | string | Parent patent applications. |
| `child` | string | Child patent applications. |
| `entity_status` | string | Legal entity status of the assignee (e.g., “small entity”, “large entity”). |
| `art_unit` | string | USPTO art unit assigned to the application. |

## CPCDefinition_database

This database is stored in Parquet format and contains the hierarchical structure, definitions, and metadata for Cooperative Patent Classification (CPC) codes. Each record represents a CPC symbol at a specific hierarchy level, with parent-child relationships, references, and descriptive titles.

### cpc_definition

File: `data/CPCDefinition/cpc_definition.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `applicationReferences` | string | Informative references to related applications. |
| `breakdownCode` | bool | Indicates whether the symbol is a breakdown code. |
| `childGroups` | string | JSON-like list of child CPC symbols at the next level. |
| `children` | string | Additional JSON-like child references. |
| `dateRevised` | double | Original numeric revision-date field; no date parsing or rescaling is performed. |
| `definition` | string | Full definition of the CPC symbol. |
| `glossary` | string | Glossary terms and explanations for the symbol. |
| `informativeReferences` | string | Additional informative references. |
| `ipcConcordant` | string | IPC concordance mapping for the CPC symbol. |
| `level` | double | Hierarchical level of the CPC symbol (e.g., 1 to 5). |
| `limitingReferences` | string | Scope-limiting references. |
| `notAllocatable` | bool | Indicates whether this symbol can be assigned to a patent. |
| `parents` | string | JSON-like list of parent CPC symbols in the hierarchy. |
| `precedenceLimitingReferences` | string | Precedence-limiting references. |
| `residualReferences` | string | Residual references for related but distinct subject matter. |
| `rules` | string | Rules for interpreting and applying the CPC symbol. |
| `scopeLimitingReferences` | string | Scope-limiting references for the symbol. |
| `status` | string | Status of the CPC symbol (e.g., “active”, “deleted”). |
| `symbol` | string | CPC classification code symbol. |
| `synonyms` | string | Synonyms for the CPC symbol. |
| `titleFull` | string | Full descriptive title of the CPC symbol. |
| `titlePart` | string | Abbreviated or partial title of the CPC symbol. |

## Representation

Structured text and natural-language dates are strings. Original hints are available in context/hints.md when enabled by the experiment.
