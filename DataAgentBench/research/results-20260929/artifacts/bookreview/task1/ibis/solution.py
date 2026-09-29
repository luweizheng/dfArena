import json
from pathlib import Path
import ibis
import ibis.expr.datatypes as dt

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
books = con.read_parquet('/workspace/data/books/books_info.parquet')
reviews = con.read_parquet('/workspace/data/review/review.parquet')

@ibis.udf.scalar.builtin
def regexp_extract_all(value: str, pattern: str, group: int) -> list[str]:
    ...

# Match calendar dates, avoiding ISBNs, page counts, and edition numbers.
months = '(?:January|February|March|April|May|June|July|August|September|October|November|December)'
pattern = rf'\b{months}\s+(?:\d{{1,2}},?\s+)?((?:1|2)\d{{3}})\b'
parsed = books.mutate(years=regexp_extract_all(books.details, pattern, 1))
# Explode all edition years and choose the earliest for each book.
years = parsed.select('book_id', year=parsed.years.unnest().cast('int64'))
earliest = years.group_by('book_id').aggregate(publication_year=years.year.min())
editions = earliest.mutate(
    join_id=earliest.book_id.re_extract(r'^bookid_(\d+)$', 1),
    decade=(earliest.publication_year // 10) * 10,
)
rated = reviews.filter(reviews.rating.notnull()).mutate(
    join_id=reviews.purchase_id.re_extract(r'^purchaseid_(\d+)$', 1)
)
joined = editions.join(rated, 'join_id')
summary = joined.group_by('decade').aggregate(
    distinct_books=joined.book_id.nunique(),
    review_count=joined.rating.count(),
    average_rating=joined.rating.mean(),
)
ranking = summary.filter(summary.distinct_books >= 10).order_by(
    ibis.desc('average_rating'), 'decade'
)
rows = ranking.to_pyarrow().to_pylist()
assert rows, 'No eligible decades'
(OUT / 'decade_ratings.json').write_text(json.dumps(rows, indent=2))
(OUT / 'answer.json').write_text(json.dumps({'answer': f"{rows[0]['decade']}s"}))
print(json.dumps(rows, indent=2))
print('Missing dates:', parsed.filter(parsed.years.length() == 0).select('book_id', 'details').to_pyarrow().to_pylist())
print('Multiple dates:', parsed.filter(parsed.years.length() > 1).select('book_id', 'details', 'years').to_pyarrow().to_pylist())
