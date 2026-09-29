# usaspending

The four original data groups are provided as local Parquet tables.

Original group names remain below to interpret the original hints. Paths are relative to this dataset root.

1. contracts_db
   - This database is provided as Parquet tables. It contains the federal contract awards registry sourced from USAspending.gov, plus a sibling table holding award amounts.
   - This database consists of two tables:
     - contracts
       - One row per contract award.
       - Fields:
         - award_id (str): Award identifier (surface form may vary per table; same canonical id may appear differently in contract_amounts and descriptions_db)
         - generated_internal_id (str): Internal USAspending identifier
         - recipient_uei (str): Unique Entity Identifier of the recipient
         - awarding_agency (str): Awarding agency
         - awarding_sub_agency (str): Awarding sub-agency
         - funding_agency (str): Funding agency
         - start_date (str): ISO date string
         - end_date (str): ISO date string
         - naics_code (str): NAICS code
         - psc_code (str): Product / Service Code
         - award_type (str): Contract type code
     - contract_amounts
       - Award amount per contract, encoded as text.
       - Fields:
         - award_id (str): Award identifier (surface forms may vary; join directly when identifiers match, and normalize only when actual differences require it)
         - amount_text (str): Dollar amount expressed numerically or through a qualitative description of monetary magnitude. For qualitative descriptions, use the text and related supplied records to assess the question's threshold; exact dollar recovery is not required.

2. recipients_db
   - This database is provided as Parquet tables. It contains the per-recipient registry derived from contract awards.
   - This database consists of one table:
     - recipients
       - One row per recipient.
       - Fields:
         - uei (str): Unique Entity Identifier
         - name (str): Recipient name
         - state (str): U.S. state of the recipient
         - n_contracts (int): Number of contract awards this recipient holds
         - total_amount_text (str): Sum of contract amounts

3. agencies_db
   - This database is provided as Parquet tables. It contains the awarding-agency reference, an agency-alias lookup, and the NAICS sector hierarchy.
   - This database consists of three tables:
     - agencies
       - One row per canonical agency.
       - Fields:
         - name (str): Canonical agency name
         - n_contracts (int): Total number of contracts awarded
         - total_amount_text (str): Total awarded amount
     - agency_aliases
       - Agency surface-form lookup.
       - Fields:
         - surface_form (str): Surface form
         - canonical_name (str): Canonical agency name
     - naics_sectors
       - NAICS code hierarchy.
       - Fields:
         - code (str): NAICS code
         - description (str): Human-readable description
         - sector (str): 2-digit parent sector code

4. descriptions_db
   - This database is provided as Parquet tables. It contains free-text contract descriptions.
   - This database consists of one collection:
     - contract_documents
       - One document per award.
       - Fields:
         - award_id (str): Award identifier
         - descriptions (JSON array text): Free-text descriptions, each with:
           - language (str): ISO language code (e.g. "en", "es")
           - value (str): Description prose

## JSON representation

The original `descriptions` list of objects is stored as a reversible JSON array string, retaining list order, object key order, language labels, and exact description text. Parse this field with a JSON parser when list/object access is needed. No translation, language correction, flattening, deduplication, or extra `_id` generation was performed. The actual BSON snapshot has only award_id and descriptions.

## Files and measured physical types

### contracts

File: `data/contracts_db/contracts.parquet`

| Column | Arrow type |
|---|---|
| `award_id` | string |
| `generated_internal_id` | string |
| `recipient_uei` | string |
| `awarding_agency` | string |
| `awarding_sub_agency` | string |
| `funding_agency` | string |
| `start_date` | string |
| `end_date` | string |
| `naics_code` | string |
| `psc_code` | string |
| `award_type` | string |

### contract_amounts

File: `data/contracts_db/contract_amounts.parquet`

| Column | Arrow type |
|---|---|
| `award_id` | string |
| `amount_text` | string |

### recipients

File: `data/recipients_db/recipients.parquet`

| Column | Arrow type |
|---|---|
| `uei` | string |
| `name` | string |
| `state` | string |
| `n_contracts` | int64 |
| `total_amount_text` | string |

### agencies

File: `data/agencies_db/agencies.parquet`

| Column | Arrow type |
|---|---|
| `name` | string |
| `n_contracts` | int32 |
| `total_amount_text` | string |

### agency_aliases

File: `data/agencies_db/agency_aliases.parquet`

| Column | Arrow type |
|---|---|
| `surface_form` | string |
| `canonical_name` | string |

### naics_sectors

File: `data/agencies_db/naics_sectors.parquet`

| Column | Arrow type |
|---|---|
| `code` | string |
| `description` | string |
| `sector` | string |

### contract_documents

File: `data/descriptions_db/contract_documents.parquet`

| Column | Arrow type |
|---|---|
| `award_id` | string |
| `descriptions` | string |

## Preservation

All original rows, duplicate entries, nulls, empty strings, amounts-as-text, date strings, identifier variants are retained. The PostgreSQL source is a literal INSERT SQL snapshot decoded without executing SQL or launching PostgreSQL. SQLite/DuckDB integer widths retain their native physical representation (SQLite INTEGER: int64; DuckDB INTEGER: int32). No fuzzy matching, normalization, amount inference, superseded-record filtering, aggregation, or answer computation has been performed. Original questions are unchanged. The hints include subsequent user-approved clarifications.
