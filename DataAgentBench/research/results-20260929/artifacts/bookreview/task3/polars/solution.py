import json
from datetime import datetime
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')

def main():
    books = pl.read_parquet('/workspace/data/books/books_info.parquet').with_columns(
        pl.col('book_id').str.extract(r'^bookid_(\d+)$', 1).alias('entity_id'),
        pl.col('categories').str.json_decode(pl.List(pl.String)).alias('category_list'),
    )
    reviews = pl.read_parquet('/workspace/data/review/review.parquet').with_columns(
        pl.col('purchase_id').str.extract(r'^purchaseid_(\d+)$', 1).alias('entity_id'),
        pl.col('review_time').str.to_datetime('%Y-%m-%d %H:%M:%S').alias('posted_at'),
    )
    # IDs use different prefixes but share the entity's numeric suffix.
    assert books['entity_id'].null_count() == 0
    assert reviews['entity_id'].null_count() == 0
    assert books['entity_id'].n_unique() == books.height
    assert reviews.join(books.select('entity_id'), on='entity_id', how='anti').height == 0
    averages = (
        reviews.filter(pl.col('posted_at') >= datetime(2020, 1, 1))
        .group_by('entity_id')
        .agg(pl.col('rating').mean().alias('average_rating'), pl.len().alias('review_count'))
    )
    result = (
        books.filter(pl.col('category_list').list.contains("Children's Books"))
        .join(averages, on='entity_id', how='inner')
        .filter(pl.col('average_rating') >= 4.5)
        .select('book_id', 'title', 'average_rating', 'review_count')
        .sort('title')
    )
    result.write_csv(OUT / 'qualifying_books.csv')
    entries = [f"{row['title']} ({row['average_rating']:.2f})" for row in result.iter_rows(named=True)]
    answer = '; '.join(entries) + '.' if entries else 'No books qualify.'
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(result.to_dicts())

if __name__ == '__main__':
    main()
