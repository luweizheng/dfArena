# agnews

The original data groups are exposed as local Parquet tables.

Original group names are retained below to interpret the original hints. Paths are relative to this dataset directory.

1. articles_database
   - This database is provided as a Parquet table and contains information about news articles. It serves as the primary source for the content of each article, including its title and description.
   - This database consists of one collection:
     - articles
       - This collection contains the actual news articles. Each document in the collection represents a single news article with its unique identifier, title, and description.
       - Fields:
         - article_id (int): Unique identifier for the article
         - title (str): Title of the news article
         - description (str): Description of the news article

2. metadata_database
   - This database is provided as Parquet tables and contains metadata about the news articles. It includes information about the authors, the regions in which the articles were published, and the publication dates.
   - This database consists of two tables:
     - authors
       - This table contains information about all authors who contributed to the articles in the articles_database.
       - Fields:
         - author_id (int): Unique identifier for the author
         - name (str): Full name of the author

     - article_metadata
       - This table contains metadata linking each article to its author and providing details about its publication. Each row represents a single article and connects it to an author and publication information.
       - Fields:
         - article_id (int): Article identifier linking to the articles collection
         - author_id (int): Author identifier linking to the authors table
         - region (str): Geographic region where the article was published
         - publication_date (str): Publication date in the format YYYY-MM-DD
The source description listed `_id`, but the actual BSON snapshot contains only article_id, title, and description. No `_id` has been generated. There is no category column; category determination remains part of the original task, as described in the optional hints.

## Files and measured physical column types

### articles

File: `data/articles/articles.parquet`

| Column | Arrow type |
|---|---|
| `article_id` | int32 |
| `title` | string |
| `description` | string |

### article_metadata

File: `data/metadata/article_metadata.parquet`

| Column | Arrow type |
|---|---|
| `article_id` | int64 |
| `author_id` | int64 |
| `region` | string |
| `publication_date` | string |

### authors

File: `data/metadata/authors.parquet`

| Column | Arrow type |
|---|---|
| `author_id` | int64 |
| `name` | string |

## Preservation

Every input row and its order are retained, including any repeated records. Strings retain their exact characters, whitespace, and line breaks. Dates remain strings. BSON int32 stays int32; SQLite INTEGER is int64. ObjectId uses the explicitly documented reversible encoding. Both BSON snapshots have the same fields present in every document and contain no nulls or nested values. Source records are not cleaned or augmented.
