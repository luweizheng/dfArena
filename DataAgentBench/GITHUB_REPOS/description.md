# GITHUB_REPOS

This dataset exposes the original two database groups as local Parquet tables.

Original group names below are retained to interpret the original hints. All file paths are relative to the dataset root.

## metadata_database

This table group is stored in Parquet format and contains metadata about GitHub repositories, including their declared programming languages, licenses, and repository-level statistics. It consists of three tables.

### languages

File: `data/metadata/languages.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `repo_name` | string | Name of the GitHub repository in `owner/repo` format. |
| `language_description` | string | Programming language(s) used in the repository, represented in natural language format. |

### licenses

File: `data/metadata/licenses.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `repo_name` | string | Name of the GitHub repository in `owner/repo` format. |
| `license` | string | License identifier associated with the repository (e.g., `apache-2.0`, `mit`). |

### repos

File: `data/metadata/repos.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `repo_name` | string | Name of the GitHub repository in `owner/repo` format. |
| `watch_count` | int64 | Number of users watching the repository on GitHub. |

## artifacts_database

This table group is stored in Parquet format and contains GitHub repository artifacts, including file contents, commit history, and file-level metadata. It consists of three tables.

### contents

File: `data/artifacts/contents.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `id` | string | Identifier of the file blob in the repository. |
| `content` | string | The file content (textual data). For large or binary files, this may contain placeholders or truncated values. |
| `sample_repo_name` | string | Name of the repository where the file resides, in `owner/repo` format. |
| `sample_ref` | string | Reference name (e.g., branch or commit SHA). |
| `sample_path` | string | Path of the file within the repository. |
| `sample_symlink_target` | string | If the file is a symlink, indicates the symlink target path. |
| `repo_data_description` | string | Natural language description summarizing the file’s metadata (derived from original size, binary, copies, and mode fields). |

### commits

File: `data/artifacts/commits.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `commit` | string | Unique identifier (SHA) of the commit. |
| `tree` | string | SHA identifier of the commit’s associated tree object. |
| `parent` | string | One or more parent commit SHAs (JSON-like format for merge commits). |
| `author` | string | JSON-like object containing author information (name, email, timestamp). |
| `committer` | string | JSON-like object containing committer information (name, email, timestamp). |
| `subject` | string | Short subject line of the commit message. |
| `message` | string | Full commit message. |
| `trailer` | string | Additional metadata fields attached to the commit (JSON-like). |
| `difference` | string | JSON-like structure representing file changes introduced by the commit. |
| `difference_truncated` | double | Indicator if the difference data is truncated. Entirely null in this snapshot; the source description calls it a boolean indicator. |
| `repo_name` | string | Repository name in `owner/repo` format. |
| `encoding` | string | Encoding format of the commit data (if applicable). |

### files

File: `data/artifacts/files.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `repo_name` | string | Name of the GitHub repository in `owner/repo` format. |
| `ref` | string | Reference name (branch or commit SHA) at which the file metadata is recorded. |
| `path` | string | Path of the file within the repository. |
| `mode` | int64 | File mode (e.g., normal file, executable, symlink). |
| `id` | string | Identifier of the file blob. |
| `symlink_target` | string | If the file is a symlink, the target path it points to. |

Additional hints are in hints.md when enabled by the experiment.
