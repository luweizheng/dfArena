from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
DATE_PATTERN = (
    r'(?i)\b(?:January|February|March|April|May|June|July|August|'
    r'September|October|November|December)\s+(?:\d{1,2},?\s+)?\d{4}\b'
)

books = pl.read_parquet(DATA / 'books/books_info.parquet')
reviews = pl.read_parquet(DATA / 'review/review.parquet')
# Match entity suffixes because the tables use bookid_ and purchaseid_ prefixes.
books = books.with_columns(
    pl.col('book_id').str.extract(r'^bookid_(\d+)$', 1).alias('entity_id'),
    pl.col('details').str.extract_all(DATE_PATTERN)
    .list.eval(pl.element().str.extract(r'(\d{4})$', 1).cast(pl.Int64))
    .list.min().alias('publication_year'),
).with_columns((pl.col('publication_year') // 10 * 10).alias('decade'))
reviews = reviews.with_columns(
    pl.col('purchase_id').str.extract(r'^purchaseid_(\d+)$', 1).alias('entity_id')
)
assert books['entity_id'].null_count() == 0
assert reviews['entity_id'].null_count() == 0
assert books['entity_id'].n_unique() == books.height
assert reviews.join(books.select('entity_id'), on='entity_id', how='anti').height == 0
joined = reviews.filter(pl.col('rating').is_not_null()).join(
    books.select('entity_id', 'book_id', 'decade'), on='entity_id', how='inner', validate='m:1'
).filter(pl.col('decade').is_not_null())
# Averaging review rows gives every individual review equal weight.
summary = joined.group_by('decade').agg(
    pl.col('book_id').n_unique().alias('distinct_rated_books'),
    pl.len().alias('reviews'),
    pl.col('rating').mean().alias('average_rating'),
).sort('average_rating', descending=True)
summary.write_csv(OUT / 'decade_summary.csv')
books.select('book_id', 'publication_year', 'decade').write_csv(OUT / 'publication_years.csv')
eligible = summary.filter(pl.col('distinct_rated_books') >= 10)
assert eligible.height > 0
answer = f"{eligible.item(0, 'decade')}s"
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(summary)
print(json.dumps({'answer': answer}))
