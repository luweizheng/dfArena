# Hints

- Some queries may require joining across tables using identifiers such as "id" or "repo_name" to correctly combine information.  
- The "languages" table's language_description field may contain multiple programming languages per repository. To determine the primary or main language, compare the relative number of bytes across languages.  
- The "contents" table's repo_data_description field contains natural language metadata derived from file attributes (e.g., size, binary, copies, mode). Some queries may rely on these attributes for filtering or interpretation.  
- When calculating the proportion of README.md files containing copyright information, include only files whose contents are provided in the dataset; files without available contents do not participate in the calculation.
- When checking whether a commit message begins with "merge", "update", or "test", compare case-insensitively.
