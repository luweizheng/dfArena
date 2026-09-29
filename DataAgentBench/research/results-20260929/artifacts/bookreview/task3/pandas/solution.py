import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
books = pd.read_parquet(DATA / 'books/books_info.parquet')
reviews = pd.read_parquet(DATA / 'review/review.parquet')
# The two identifier namespaces share the same entity suffix.
books['entity_id'] = books['book_id'].str.extract(r'^bookid_(\d+)$', expand=False)
reviews['entity_id'] = reviews['purchase_id'].str.extract(r'^purchaseid_(\d+)$', expand=False)
assert books['entity_id'].notna().all() and reviews['entity_id'].notna().all()
assert books['entity_id'].is_unique
assert reviews['entity_id'].isin(books['entity_id']).all()
children = books[books['categories'].map(lambda value: "Children's Books" in json.loads(value))]
reviews['date'] = pd.to_datetime(reviews['review_time'], errors='raise')
recent = reviews[reviews['date'] >= pd.Timestamp('2020-01-01')]
averages = recent.groupby('entity_id', as_index=False).agg(average_rating=('rating', 'mean'), review_count=('rating', 'count'))
result = children.merge(averages, on='entity_id', validate='one_to_one')
result = result.loc[result['average_rating'] >= 4.5, ['book_id', 'title', 'average_rating', 'review_count']].sort_values(['title', 'book_id'])
result.to_csv(OUT / 'qualifying_books.csv', index=False)
answer = '; '.join(f"{row.title.strip()} (average rating: {row.average_rating:g})" for row in result.itertuples(index=False))
if not answer:
    answer = 'No books qualify.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(result.to_string(index=False))
