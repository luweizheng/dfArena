# googlelocal

The original two data groups are provided as local Parquet tables. They contain Google Maps reviews and business metadata collected up to September 2021 in the United States. Original group names are retained for interpreting the original hints. All file paths are relative to this dataset root.

## review_database

### review

Google Maps review information, including reviewer names, ratings, and text.

File: `data/review/review.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `name` | string | Name of the reviewer |
| `time` | string | Timestamp of the review |
| `rating` | int64 | Rating given by the reviewer (1-5 scale) |
| `text` | string | Review text content |
| `gmap_id` | string | Google Maps business identifier |

## business_database

### business_description

Google Maps business metadata, including names, descriptions, and operating hours.

File: `data/business/business_description.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `name` | string | Business name |
| `gmap_id` | string | Google Maps business identifier (links to review_database) |
| `description` | string | Business description |
| `num_of_reviews` | int64 | Total number of reviews for this business |
| `hours` | string | Operating hours information; stored as structured text |
| `MISC` | string | Additional miscellaneous business information; stored as structured text |
| `state` | string | Business operating status (e.g., open, closed, temporarily closed) |

## Representation

Structured text, bracketed annotations, and date-like or number-like text are strings. Additional guidance is in hints.md when enabled by the experiment configuration.
