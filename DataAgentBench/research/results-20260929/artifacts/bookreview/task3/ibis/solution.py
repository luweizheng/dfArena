import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    books = con.read_parquet('/workspace/data/books/books_info.parquet')
    reviews = con.read_parquet('/workspace/data/review/review.parquet')
    # The same entity has bookid_ and purchaseid_ prefixes in the two tables.
    children = books.filter(books.categories.contains('"Children\'s Books"')).mutate(
        entity_id=books.book_id.re_extract(r'^bookid_(\d+)$', 1)
    )
    recent = reviews.mutate(
        reviewed_at=reviews.review_time.cast('timestamp'),
        entity_id=reviews.purchase_id.re_extract(r'^purchaseid_(\d+)$', 1),
    )
    recent = recent.filter(recent.reviewed_at >= ibis.timestamp('2020-01-01'))
    averages = recent.group_by('entity_id').aggregate(
        average_rating=recent.rating.mean(), review_count=recent.count()
    )
    result = children.join(averages, 'entity_id').filter(
        averages.average_rating >= 4.5
    ).select(children.book_id, children.title, averages.average_rating, averages.review_count)
    rows = result.order_by('title', 'book_id').to_pyarrow().to_pylist()
    Path('/workspace/work/results.json').write_text(json.dumps(rows, indent=2))
    answer = '; '.join(f"{row['title']} (average rating: {row['average_rating']:.2f})" for row in rows)
    if not rows:
        answer = 'No books meet the criteria.'
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False))
    print(json.dumps({'answer': answer}, ensure_ascii=False))


if __name__ == '__main__':
    main()
