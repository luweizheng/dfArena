# civic_unstructured

The original data groups are exposed as local Parquet tables.

Original group names are retained below to interpret the original hints. Paths are relative to this dataset directory.

## civic_docs_database

This database is provided as a Parquet table and contains Malibu city council meeting agendas.

### civic_docs

This collection contains 19 documents, one per city council meeting agenda. Each document covers multiple civic projects and their current status at the time of the meeting.

File: `data/civic_docs/civic_docs.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `_id` | string | Original MongoDB ObjectId encoded reversibly as 24 lowercase hexadecimal characters; not a new identifier |
| `report_id` | string | Sequential report identifier (e.g., "rid_0001", "rid_0002", ..., "rid_0019") |
| `report_content` | string | Full plain-text content of the meeting agenda, describing multiple civic projects. |

## funding_database

This database is provided as a Parquet table and contains structured funding records for civic projects.

### Funding

This table contains funding grant records.

File: `data/funding/Funding.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `fid` | string | Unique funding record identifier |
| `project_name` | string | Name of the project receiving the grant |
| `funding_source` | string | Source of the funding |
| `grant_time` | string | Date the funding was granted |
| `amount` | int64 | Funding amount in USD |

## Representation

Dates are strings. Each agenda is one complete text cell; project extraction and matching are part of the tasks.
