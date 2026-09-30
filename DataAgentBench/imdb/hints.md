# Hints

- Many identifier columns in both databases use non-standard string encodings rather than plain integers. To join across tables, you must extract the embedded numeric ID by stripping the alphabetic prefix, any punctuation padding characters, and any leading zeros. For example, `tt0000042` → `42`, `nm001` → `1`, `InfT~~7` → `7`. This applies to the following columns: title.id, company_name.id, movie_companies.id, name.id, cast_info.person_id, keyword.id, movie_keyword.keyword_id, info_type.id, movie_info.info_type_id, and role_type.id.
- When checking whether an actress's name contains "An", compare case-sensitively.
- For the query requesting the alphabetically first alternate name, character name, actress name, and title, include all title types in the title table, such as movies, TV series, and TV episodes; do not restrict the scope to kind "movie".
