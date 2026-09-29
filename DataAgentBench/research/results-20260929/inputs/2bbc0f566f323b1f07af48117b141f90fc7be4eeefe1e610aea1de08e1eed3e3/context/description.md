# GITHUB_REPOS

This dataset exposes the original two database groups as local Parquet tables.

Original group names below are retained to interpret the original hints. All file paths are relative to the dataset root.

1. metadata_database  
   - This table group is stored in Parquet format and contains metadata about GitHub repositories, including their declared programming languages, licenses, and repository-level statistics. It consists of three tables:  
   - This database consists of three tables:
    - languages  
      - Fields:  
        - repo_name (str): Name of the GitHub repository in `owner/repo` format.  
        - language_description (str): Programming language(s) used in the repository, represented in natural language format.  

    - licenses  
      - Fields:  
        - repo_name (str): Name of the GitHub repository in `owner/repo` format.  
        - license (str): License identifier associated with the repository (e.g., `apache-2.0`, `mit`).  

    - repos  
      - Fields:  
        - repo_name (str): Name of the GitHub repository in `owner/repo` format.  
        - watch_count (int): Number of users watching the repository on GitHub.  


2. artifacts_database  
   - This table group is stored in Parquet format and contains GitHub repository artifacts, including file contents, commit history, and file-level metadata. It consists of three tables:  
   - This database consists of three tables:
    - contents  
      - Fields:  
        - id (str): Identifier of the file blob in the repository.  
        - content (str): The file content (textual data). For large or binary files, this may contain placeholders or truncated values.  
        - sample_repo_name (str): Name of the repository where the file resides, in `owner/repo` format.  
        - sample_ref (str): Reference name (e.g., branch or commit SHA).  
        - sample_path (str): Path of the file within the repository.  
        - sample_symlink_target (str): If the file is a symlink, indicates the symlink target path.  
        - repo_data_description (str): Natural language description summarizing the file’s metadata (derived from original size, binary, copies, and mode fields).  

    - commits  
      - Fields:  
        - commit (str): Unique identifier (SHA) of the commit.  
        - tree (str): SHA identifier of the commit’s associated tree object.  
        - parent (str): One or more parent commit SHAs (JSON-like format for merge commits).  
        - author (str): JSON-like object containing author information (name, email, timestamp).  
        - committer (str): JSON-like object containing committer information (name, email, timestamp).  
        - subject (str): Short subject line of the commit message.  
        - message (str): Full commit message.  
        - trailer (str): Additional metadata fields attached to the commit (JSON-like).  
        - difference (str): JSON-like structure representing file changes introduced by the commit.  
        - difference_truncated (double, all null in this snapshot): Indicator if the difference data is truncated.  
        - repo_name (str): Repository name in `owner/repo` format.  
        - encoding (str): Encoding format of the commit data (if applicable).  

    - files  
      - Fields:  
        - repo_name (str): Name of the GitHub repository in `owner/repo` format.  
        - ref (str): Reference name (branch or commit SHA) at which the file metadata is recorded.  
        - path (str): Path of the file within the repository.  
        - mode (int): File mode (e.g., normal file, executable, symlink).  
        - id (str): Identifier of the file blob.  
        - symlink_target (str): If the file is a symlink, the target path it points to.  

## Files and physical types

- `languages`: `data/metadata/languages.parquet`. `repo_name` = string, `language_description` = string.
- `licenses`: `data/metadata/licenses.parquet`. `repo_name` = string, `license` = string.
- `repos`: `data/metadata/repos.parquet`. `repo_name` = string, `watch_count` = int64.
- `commits`: `data/artifacts/commits.parquet`. `commit` = string, `tree` = string, `parent` = string, `author` = string, `committer` = string, `subject` = string, `message` = string, `trailer` = string, `difference` = string, `difference_truncated` = double, `repo_name` = string, `encoding` = string.
- `contents`: `data/artifacts/contents.parquet`. `id` = string, `content` = string, `sample_repo_name` = string, `sample_ref` = string, `sample_path` = string, `sample_symlink_target` = string, `repo_data_description` = string.
- `files`: `data/artifacts/files.parquet`. `repo_name` = string, `ref` = string, `path` = string, `mode` = int64, `id` = string, `symlink_target` = string.

The original description calls difference_truncated a boolean indicator, but the actual column is DOUBLE and all of its values are null. This source representation is preserved. Content, commit metadata, language descriptions, and JSON-like strings remain text; no text is executed or parsed during migration.

## Preservation

All original records, duplicates, nulls, empty strings, and text formatting are retained. Dates remain strings; numeric values are not rounded. No joins, deduplication, missing-value imputation, or ground-truth computation are performed. metadata.yaml lists every table with its original name, exact local path, physical column types, row count, and checksum. Additional original hints are in context/hints.md when enabled by the experiment.
