import json
import re
from pathlib import Path
import pandas as pd

OUT = Path('/workspace/work')
books = pd.read_parquet('/workspace/data/books/books_info.parquet')
reviews = pd.read_parquet('/workspace/data/review/review.parquet', columns=['purchase_id', 'rating'])
# The two tables encode the same entity with different identifier prefixes.
books['entity_id'] = books['book_id'].str.extract(r'^bookid_(\d+)$', expand=False)
reviews['entity_id'] = reviews['purchase_id'].str.extract(r'^purchaseid_(\d+)$', expand=False)
assert books['entity_id'].notna().all() and books['entity_id'].is_unique
assert reviews['entity_id'].notna().all()
assert reviews['entity_id'].isin(books['entity_id']).all()

# Match dates rather than arbitrary four-digit numbers (ISBNs, file sizes, etc.).
date_pattern = re.compile(
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+(?:\d{1,2},?\s+)?(\d{4})\b'
)
def publication_year(details):
    years = [int(y) for y in date_pattern.findall(details or '')]
    return min(years) if years else pd.NA

books['publication_year'] = books['details'].map(publication_year).astype('Int64')
books['decade'] = (books['publication_year'] // 10) * 10
rated = reviews.dropna(subset=['rating']).merge(
    books[['entity_id', 'book_id', 'decade']], on='entity_id', validate='many_to_one'
).dropna(subset=['decade'])
# Aggregate review rows directly, giving each individual review equal weight.
summary = rated.groupby('decade').agg(
    distinct_books=('book_id', 'nunique'),
    review_count=('rating', 'size'),
    average_rating=('rating', 'mean'),
)
eligible = summary.loc[summary['distinct_books'] >= 10].sort_values('average_rating', ascending=False)
assert not eligible.empty
winner = int(eligible.index[0])
summary.to_csv(OUT / 'decade_summary.csv')
books[['book_id', 'publication_year', 'decade']].to_csv(OUT / 'publication_years.csv', index=False)
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{winner}s'}) + '\n')
print(summary.to_string())
print((OUT / 'answer.json').read_text())
