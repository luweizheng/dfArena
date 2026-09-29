# music_brainz_20k

This dataset contains two Parquet tables: music-track records and individual sales transactions. Paths below are relative to the dataset root.

## Table: `tracks`

File: `data/tracks/tracks.parquet`

Detailed information about music tracks, including title, artist and album. Each row represents a track record with a unique `track_id`; the table may contain multiple records for the same real-world track originating from different sources.

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `track_id` | `int64` | Unique identifier for a track record in this table. |
| `source_id` | `int64` | Identifier of the source from which the record originates. |
| `source_track_id` | `string` | Original track identifier from the source; uniqueness is not guaranteed. |
| `title` | `string` | Track title. |
| `artist` | `string` | Artist or band name. |
| `album` | `string` | Album in which the track appears. |
| `year` | `string` | Year of publication. |
| `length` | `string` | Track length, in seconds or a formatted string. |
| `language` | `string` | Track language. |

## Table: `sales`

File: `data/sales/sales.parquet`

Individual sales transactions for track records. Each row represents a sale for a specific `track_id`.

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `sale_id` | `int32` | Unique identifier for a sale record. |
| `track_id` | `int32` | Identifier linking the sale to a record in `tracks`. |
| `country` | `string` | Country in which the sale occurred. |
| `store` | `string` | Store or platform where the sale occurred. |
| `units_sold` | `int32` | Number of units sold in the transaction. |
| `revenue_usd` | `double` | Revenue generated in USD from the sale. |

## Relationships and representation

`sales.track_id` links to `tracks.track_id`. A track record and a real-world song are not necessarily the same unit of analysis.

Additional guidance is available in `context/hints.md` when enabled by the experiment configuration.
