import json
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    books = pl.read_parquet(ROOT / 'books/books_info.parquet').with_columns(
        pl.col('book_id').str.extract(r'^bookid_(\d+)$', 1).alias('entity_id')
    )
    reviews = pl.read_parquet(ROOT / 'review/review.parquet').with_columns(
        pl.col('purchase_id').str.extract(r'^purchaseid_(\d+)$', 1).alias('entity_id')
    )
    assert books['entity_id'].null_count() == 0
    assert reviews['entity_id'].null_count() == 0
    assert books['entity_id'].n_unique() == books.height
    assert reviews.join(books.select('entity_id'), on='entity_id', how='anti').height == 0
    averages = reviews.group_by('entity_id').agg(
        pl.col('rating').mean().alias('average_rating'),
        pl.col('rating').count().alias('review_count'),
    )
    matches = (
        books.filter(
            pl.col('categories').str.contains(r'''["']Literature & Fiction["']''')
            & pl.col('details').str.contains(r'(?i)\bEnglish\b')
        )
        .join(averages, on='entity_id', how='inner')
        .filter(pl.col('average_rating') == 5.0)
        .select('book_id', 'title', 'average_rating', 'review_count')
        .sort('title')
    )
    matches.write_csv(OUT / 'matching_books.csv')
    titles = matches['title'].to_list()
    answer = '; '.join(titles) if titles else 'No matching books.'
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(matches.to_dicts())

if __name__ == '__main__':
    main()
