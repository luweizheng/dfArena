# imdb

The two original data groups are provided as local Parquet tables.

Original group names are retained below. Paths are relative to this dataset root.

## movies_database

This database is provided as Parquet tables and contains movie-centric information. It covers titles, production companies, keywords, genres, ratings, and structural relationships between titles.

### title

This table is the central table of the movies_database. Each row represents a unique title entry (movie, TV series, episode, video game, etc.).

File: `data/movies/title.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | string | Unique identifier for the title. |
| `title` | string | The title string of the movie or show. |
| `imdb_index` | string | Disambiguation suffix used by IMDB (e.g., Roman numerals). |
| `kind_id` | int32 | Foreign key referencing kind_type.id; indicates the type of title. |
| `production_year` | int32 | Year in which the title was produced or released. |
| `imdb_id` | int32 | Original numeric IMDB identifier. |
| `phonetic_code` | string | Phonetic encoding of the title for search purposes. |
| `episode_of_id` | int32 | For TV episodes, references the id of the parent series in this table. |
| `season_nr` | int32 | Season number (for TV episodes). |
| `episode_nr` | int32 | Episode number within a season. |
| `series_years` | string | Year span for TV series (e.g., "1990-1995"). |
| `md5sum` | string | MD5 checksum of the record. |

### aka_title

This table stores alternate or foreign-language titles for movies and shows.

File: `data/movies/aka_title.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier for the alternate title record. |
| `movie_id` | int32 | Foreign key referencing title.id. |
| `title` | string | The alternate title string. |
| `imdb_index` | string | Disambiguation suffix. |
| `kind_id` | int32 | Foreign key referencing kind_type.id. |
| `production_year` | int32 | Production year for this alternate release. |
| `phonetic_code` | string | Phonetic encoding of the alternate title. |
| `episode_of_id` | int32 | Parent series ID for episode alternate titles. |
| `season_nr` | int32 | Season number. |
| `episode_nr` | int32 | Episode number. |
| `note` | string | Notes on context (e.g., country, dubbed version). |
| `md5sum` | string | MD5 checksum. |

### kind_type

This lookup table enumerates the types of titles (e.g., movie, TV series, episode).

File: `data/movies/kind_type.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier. |
| `kind` | string | Label for the title type (e.g., "movie", "tv series", "episode"). |

### movie_info

This table stores free-text metadata about movies, such as genres, languages, countries, plot summaries, and technical specifications.

File: `data/movies/movie_info.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier for the info record. |
| `movie_id` | int32 | Foreign key referencing title.id. |
| `info_type_id` | string | Foreign key referencing info_type.id. |
| `info` | string | The metadata value (e.g., "English", "USA", "Drama"). |
| `note` | string | Supplemental notes. |

### movie_info_idx

This table stores indexed numeric metadata about movies, primarily ratings and vote counts.

File: `data/movies/movie_info_idx.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier for the index record. |
| `movie_id` | int32 | Foreign key referencing title.id. |
| `info_type_id` | int32 | Foreign key referencing info_type.id. |
| `info` | string | The numeric metadata value (e.g., a rating score). |
| `note` | string | Supplemental notes. |

### info_type

This lookup table enumerates the categories of metadata stored in movie_info and movie_info_idx (e.g., "genres", "rating", "votes").

File: `data/movies/info_type.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | string | Unique identifier. |
| `info` | string | Description of the info category (e.g., "genres", "rating", "languages"). |

### movie_keyword

This table records the association between movies and descriptive keywords.

File: `data/movies/movie_keyword.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier for the movie-keyword association. |
| `movie_id` | int32 | Foreign key referencing title.id. |
| `keyword_id` | string | Foreign key referencing keyword.id. |

### keyword

This lookup table contains all descriptive keywords (tags) used to annotate movies.

File: `data/movies/keyword.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | string | Unique identifier. |
| `keyword` | string | The keyword text (e.g., "murder", "based-on-novel"). |
| `phonetic_code` | string | Phonetic encoding of the keyword. |

### movie_companies

This table links movies to the production or distribution companies involved.

File: `data/movies/movie_companies.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | string | Unique identifier. |
| `movie_id` | int32 | Foreign key referencing title.id. |
| `company_id` | int32 | Foreign key referencing company_name.id. |
| `company_type_id` | int32 | Foreign key referencing company_type.id. |
| `note` | string | Additional notes on the company's role. |

### company_name

This lookup table contains names and metadata for production and distribution companies.

File: `data/movies/company_name.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | string | Unique identifier. |
| `name` | string | Full name of the company. |
| `country_code` | string | Country code of the company (e.g., "[us]", "[gb]"). |
| `imdb_id` | int32 | Original IMDB numeric identifier. |
| `name_pcode_nf` | string | Phonetic code for the company name. |
| `name_pcode_sf` | string | Alternate phonetic code. |
| `md5sum` | string | MD5 checksum. |

### company_type

This lookup table enumerates the roles a company can have (e.g., production, distribution).

File: `data/movies/company_type.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier. |
| `kind` | string | Company role label (e.g., "production companies", "distributors"). |

### movie_link

This table records directional relationships between titles (e.g., sequel, remake, spin-off).

File: `data/movies/movie_link.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier. |
| `movie_id` | int32 | Foreign key referencing title.id (the source title). |
| `linked_movie_id` | int32 | Foreign key referencing title.id (the related title). |
| `link_type_id` | int32 | Foreign key referencing link_type.id. |

### link_type

This lookup table enumerates the types of relationships between titles.

File: `data/movies/link_type.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier. |
| `link` | string | Relationship description (e.g., "follows", "sequel", "remake of"). |

### complete_cast

This table records the completeness status of cast and crew information for a movie.

File: `data/movies/complete_cast.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier. |
| `movie_id` | int32 | Foreign key referencing title.id. |
| `subject_id` | int32 | Foreign key referencing comp_cast_type.id; indicates whether cast or crew is being described. |
| `status_id` | int32 | Foreign key referencing comp_cast_type.id; indicates the completeness status. |

### comp_cast_type

This lookup table enumerates the subjects and statuses used in complete_cast.

File: `data/movies/comp_cast_type.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int32 | Unique identifier. |
| `kind` | string | Label for the subject or status (e.g., "cast", "crew", "complete", "complete+verified"). |

## people_database

This database is provided as Parquet tables and contains people-centric information from IMDB. It covers individuals who worked on movies (actors, directors, writers, etc.), their alternate names, roles, biographical information, and their casting associations with titles.

### name

This table is the central table of the people_database. Each row represents a unique person in the IMDB database.

File: `data/people/name.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | string | Unique identifier. |
| `name` | string | Full name of the person (last name, first name format). |
| `imdb_index` | string | Disambiguation suffix for persons sharing the same name. |
| `imdb_id` | int64 | Original IMDB numeric identifier. |
| `gender` | string | Gender of the person ("m" or "f"). |
| `name_pcode_cf` | string | Phonetic code for the full name. |
| `name_pcode_nf` | string | Alternate phonetic code. |
| `surname_pcode` | string | Phonetic code for the surname. |
| `md5sum` | string | MD5 checksum. |

### aka_name

This table stores alternate names or pseudonyms for people.

File: `data/people/aka_name.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int64 | Unique identifier. |
| `person_id` | int64 | Foreign key referencing name.id. |
| `name` | string | The alternate name or pseudonym. |
| `imdb_index` | string | Disambiguation suffix. |
| `name_pcode_cf` | string | Phonetic code. |
| `name_pcode_nf` | string | Alternate phonetic code. |
| `surname_pcode` | string | Phonetic code for the surname. |
| `md5sum` | string | MD5 checksum. |

### cast_info

This table records the association between a person and a movie in a specific role. It is the central join table linking people_database to movies_database.

File: `data/people/cast_info.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int64 | Unique identifier. |
| `person_id` | string | Foreign key referencing name.id. |
| `movie_id` | int64 | Foreign key referencing title.id in movies_database. |
| `person_role_id` | int64 | Foreign key referencing char_name.id; the character played. |
| `note` | string | Additional credit notes (e.g., "uncredited"). |
| `nr_order` | int64 | Billing order of the credit. |
| `role_id` | int64 | Foreign key referencing role_type.id. |

### char_name

This table contains character names that appear in movie credits.

File: `data/people/char_name.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int64 | Unique identifier. |
| `name` | string | The character name. |
| `imdb_index` | string | Disambiguation suffix. |
| `imdb_id` | int64 | Original IMDB numeric identifier. |
| `name_pcode_nf` | string | Phonetic code. |
| `surname_pcode` | string | Phonetic code for the surname portion. |
| `md5sum` | string | MD5 checksum. |

### person_info

This table stores biographical and career metadata about people (e.g., birth date, birthplace, trivia).

File: `data/people/person_info.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | int64 | Unique identifier. |
| `person_id` | int64 | Foreign key referencing name.id. |
| `info_type_id` | int64 | Foreign key referencing info_type.id in movies_database. |
| `info` | string | The metadata value. |
| `note` | string | Supplemental notes. |

### role_type

This lookup table enumerates the types of roles a person can have in a movie (e.g., actor, director, writer).

File: `data/people/role_type.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | string | Unique identifier. |
| `role` | string | Role description (e.g., "actor", "director", "writer", "producer"). |

## Representation

Text fields are strings, including numeric-looking values and encoded identifiers.
