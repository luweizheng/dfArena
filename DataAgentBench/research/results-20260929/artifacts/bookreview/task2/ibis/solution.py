import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    books = con.read_parquet('/workspace/data/books/books_info.parquet')
    reviews = con.read_parquet('/workspace/data/review/review.parquet')
    # The table-specific prefixes differ; the suffix identifies the same entity.
    books = books.mutate(entity_id=books.book_id.re_replace(r'^bookid_', ''))
    reviews = reviews.mutate(entity_id=reviews.purchase_id.re_replace(r'^purchaseid_', ''))
    averages = reviews.group_by('entity_id').aggregate(
        average_rating=reviews.rating.mean(), review_count=reviews.rating.count()
    )
    eligible = books.filter(
        books.categories.contains('"Literature & Fiction"'),
        books.details.lower().re_search(r'\benglish\b'),
    )
    matches = (
        eligible.join(averages, 'entity_id')
        .filter(averages.average_rating == 5.0)
        .select('book_id', 'title', 'average_rating', 'review_count')
        .distinct()
        .order_by('title', 'book_id')
    )
    rows = matches.to_pyarrow().to_pylist()
    out = Path('/workspace/work')
    (out / 'matching_books.json').write_text(json.dumps(rows, indent=2))
    answer = 'Books with an average rating of 5.0: ' + '; '.join(row['title'] for row in rows) + '.'
    (out / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False))
    print(json.dumps({'matching_books': len(rows), 'answer': answer}, ensure_ascii=False))


if __name__ == '__main__':
    main()
