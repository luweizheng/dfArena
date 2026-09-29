# agnews

The original data groups are exposed as local Parquet tables.

Original group names are retained below to interpret the original hints. Paths are relative to this dataset directory.

## articles_database

This database is provided as a Parquet table and contains information about news articles. It serves as the primary source for the content of each article, including its title and description.

### articles

This collection contains the actual news articles. Each document in the collection represents a single news article with its unique identifier, title, and description.

File: `data/articles/articles.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `article_id` | int32 | Unique identifier for the article |
| `title` | string | Title of the news article |
| `description` | string | Description of the news article |

The source description listed `_id`, but the actual BSON snapshot contains only article_id, title, and description. There is no category column; category determination remains part of the original task, as described in the optional hints.

## metadata_database

This database is provided as Parquet tables and contains metadata about the news articles. It includes information about the authors, the regions in which the articles were published, and the publication dates.

### authors

This table contains information about all authors who contributed to the articles in the articles_database.

File: `data/metadata/authors.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `author_id` | int64 | Unique identifier for the author |
| `name` | string | Full name of the author |

### article_metadata

This table contains metadata linking each article to its author and providing details about its publication. Each row represents a single article and connects it to an author and publication information.

File: `data/metadata/article_metadata.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `article_id` | int64 | Article identifier linking to the articles collection |
| `author_id` | int64 | Author identifier linking to the authors table |
| `region` | string | Geographic region where the article was published |
| `publication_date` | string | Publication date in the format YYYY-MM-DD |

## Representation

Dates are strings. Both document tables have the same fields in every row and contain no nulls or nested values.
