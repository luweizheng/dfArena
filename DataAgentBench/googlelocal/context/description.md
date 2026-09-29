# googlelocal

The original data groups are provided as local Parquet tables.

Original group names remain below for interpreting the original hints. Paths are relative to this dataset directory.

1. review_database
   - This database is stored in Parquet format and contains review information from Google Maps (reviewer name, ratings, text, etc.) collected up to September 2021 in the United States.
   - This database consists of one table:
    - review:
      - Fields:
        - name (str): Name of the reviewer
        - time (str): Timestamp of the review
        - rating (int): Rating given by the reviewer (1-5 scale)
        - text (str): Review text content
        - gmap_id (str): Google Maps business identifier

2. business_database
   - This database is stored in Parquet format and contains business metadata from Google Maps (business name, description, hours, etc.) collected up to September 2021 in the United States.
   - This database consists of one table:
    - business_description
      - Fields:
        - name (str): Business name
        - gmap_id (str): Google Maps business identifier (links to review_database)
        - description (str): Business description
        - num_of_reviews (int): Total number of reviews for this business
        - hours (string containing structured text): Operating hours information
        - MISC (string containing structured text): Additional miscellaneous business information
        - state (str): Business operating status (e.g., open, closed, temporarily closed)

## Files and physical column types

### business_description

File: `data/business/business_description.parquet`

| Column | Arrow type |
|---|---|
| `name` | string |
| `gmap_id` | string |
| `description` | string |
| `num_of_reviews` | int64 |
| `hours` | string |
| `MISC` | string |
| `state` | string |

### review

File: `data/review/review.parquet`

| Column | Arrow type |
|---|---|
| `name` | string |
| `time` | string |
| `rating` | int64 |
| `text` | string |
| `gmap_id` | string |

## Preservation

Original rows, duplicate records, nulls, empty strings, numeric values, column names, and text formatting are preserved. Structured text is not parsed or normalized. Textual markers such as bracketed annotations remain strings and are not replaced with nulls. Date-like and number-like text remains text. No joins, sample selection, aggregation, missing-value imputation, or answer computation has been performed. Additional original guidance is in context/hints.md when enabled by the experiment configuration.
