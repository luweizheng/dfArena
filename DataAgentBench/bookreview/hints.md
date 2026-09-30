# Hints 

- In books_info, the "description", "categories", and "features" content appears to be in list or dictionary format, but they are actually stored as strings in the Parquet table.
- The fields "book_id" in books_info and "purchase_id" in review refer to the same book entities across different tables. While the field names are not exact matches, they can be joined using a fuzzy join approach to solve the query.
- For some queries, you could get needed information from "categories" or "details" columns in books_info.

## Clarification for task1

When calculating the average rating, each individual review has equal weight. Determine the publication decade using the publication date of the edition corresponding to the book entry in the provided data; if there are multiple editions, use the earliest published edition.
