# usaspending

The four original data groups are provided as local Parquet tables. Original group names are retained for interpreting the original hints. All file paths are relative to this dataset root.

## contracts_db

Federal contract awards registry sourced from USAspending.gov, plus a sibling table holding award amounts.

### contracts

One row per contract award.

File: `data/contracts_db/contracts.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `award_id` | string | Award identifier (surface form may vary per table; same canonical id may appear differently in contract_amounts and descriptions_db) |
| `generated_internal_id` | string | Internal USAspending identifier |
| `recipient_uei` | string | Unique Entity Identifier of the recipient |
| `awarding_agency` | string | Awarding agency |
| `awarding_sub_agency` | string | Awarding sub-agency |
| `funding_agency` | string | Funding agency |
| `start_date` | string | ISO date string |
| `end_date` | string | ISO date string |
| `naics_code` | string | NAICS code |
| `psc_code` | string | Product / Service Code |
| `award_type` | string | Contract type code |

### contract_amounts

Award amount per contract, encoded as text.

File: `data/contracts_db/contract_amounts.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `award_id` | string | Award identifier (surface forms may vary; join directly when identifiers match, and normalize only when actual differences require it) |
| `amount_text` | string | Dollar amount expressed numerically or through a qualitative description of monetary magnitude. For qualitative descriptions, use the text and related supplied records to assess the question's threshold; exact dollar recovery is not required. |

## recipients_db

Per-recipient registry derived from contract awards.

### recipients

One row per recipient.

File: `data/recipients_db/recipients.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `uei` | string | Unique Entity Identifier |
| `name` | string | Recipient name |
| `state` | string | U.S. state of the recipient |
| `n_contracts` | int64 | Number of contract awards this recipient holds |
| `total_amount_text` | string | Sum of contract amounts |

## agencies_db

Awarding-agency reference, agency-alias lookup, and NAICS sector hierarchy.

### agencies

One row per canonical agency.

File: `data/agencies_db/agencies.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `name` | string | Canonical agency name |
| `n_contracts` | int32 | Total number of contracts awarded |
| `total_amount_text` | string | Total awarded amount |

### agency_aliases

Agency surface-form lookup.

File: `data/agencies_db/agency_aliases.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `surface_form` | string | Surface form |
| `canonical_name` | string | Canonical agency name |

### naics_sectors

NAICS code hierarchy.

File: `data/agencies_db/naics_sectors.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `code` | string | NAICS code |
| `description` | string | Human-readable description |
| `sector` | string | 2-digit parent sector code |

## descriptions_db

Free-text contract descriptions.

### contract_documents

One document per award.

File: `data/descriptions_db/contract_documents.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `award_id` | string | Award identifier |
| `descriptions` | string | Free-text descriptions stored as JSON array text; each item has the fields below |

Each description item contains:

- `language` (string): ISO language code (e.g. "en", "es")
- `value` (string): Description prose

## JSON representation

`descriptions` preserves the list of objects as JSON array text, including list order, duplicate entries, object key order, language labels, and exact description text. Parse non-null cells with a JSON parser for list/object access. This table has no `_id` column.

## Representation

Amounts-as-text, date strings, and identifier variants are present in the input. Task-specific clarifications are in context/hints.md.
