# bookreview

This dataset contains two Parquet tables. Paths below are relative to the dataset root.

## Table: `books_info`

Amazon book information up to 2023, including descriptions, prices, details, and titles.

File: `data/books/books_info.parquet`

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `title` | `string` | Book title |
| `subtitle` | `string` | Book subtitle |
| `author` | `string` | Book author(s) |
| `rating_number` | `int64` | Total number of ratings received |
| `features` | `string` | Book features (stored as string representation of list/dict) |
| `description` | `string` | Book description (stored as string representation of list/dict) |
| `price` | `double` | Book price |
| `store` | `string` | Store information |
| `categories` | `string` | Book categories (stored as string representation of list/dict) |
| `details` | `string` | Additional book details |
| `book_id` | `string` | Unique book identifier |

## Table: `review`

Amazon book reviews up to 2023, including ratings, review text, and helpfulness votes.

File: `data/review/review.parquet`

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `rating` | `int64` | Rating given by reviewer (1.0-5.0 scale) |
| `title` | `string` | Review Title |
| `text` | `string` | Review text content |
| `review_time` | `string` | Timestamp when review was posted |
| `helpful_vote` | `int64` | Number of helpful votes received |
| `verified_purchase` | `int64` | Whether purchase was verified |
| `purchase_id` | `string` | Unique identifier linking to book_id in books_info table |

The source describes `verified_purchase` as a boolean. The SQLite values are preserved using their exported physical type; no boolean normalization is applied.
