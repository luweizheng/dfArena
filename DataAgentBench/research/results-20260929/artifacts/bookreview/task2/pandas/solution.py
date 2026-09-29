import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
books = pd.read_parquet(DATA / 'books/books_info.parquet')
reviews = pd.read_parquet(DATA / 'review/review.parquet', columns=['purchase_id', 'rating'])
# IDs share a numeric entity suffix, with different table-specific prefixes.
books['entity_id'] = books['book_id'].str.extract(r'^bookid_(\d+)$', expand=False)
reviews['entity_id'] = reviews['purchase_id'].str.extract(r'^purchaseid_(\d+)$', expand=False)
assert books['entity_id'].notna().all() and reviews['entity_id'].notna().all()
assert books['entity_id'].is_unique
assert reviews['entity_id'].isin(books['entity_id']).all()
averages = reviews.groupby('entity_id')['rating'].agg(average_rating='mean', review_count='count')
books = books.join(averages, on='entity_id', validate='one_to_one')
is_literature = books['categories'].map(lambda value: 'Literature & Fiction' in json.loads(value) if pd.notna(value) else False)
is_english = books['details'].str.contains(r'\bEnglish\b', case=False, regex=True, na=False)
result = books.loc[is_literature & is_english & books['average_rating'].eq(5.0)].sort_values('title')
result[['book_id', 'title', 'details', 'average_rating', 'review_count']].to_json(OUT / 'matching_books.json', orient='records', indent=2)
answer = '; '.join(result['title'].tolist())
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(result[['title', 'average_rating', 'review_count']].to_string(index=False))
print('Matching books:', len(result))
print(result[['title','details']].to_string(index=False))
