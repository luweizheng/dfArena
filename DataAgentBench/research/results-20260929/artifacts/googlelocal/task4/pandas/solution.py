import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
reviews = pd.read_parquet(DATA / 'review/review.parquet', columns=['time', 'rating', 'gmap_id'])
businesses = pd.read_parquet(DATA / 'business/business_description.parquet', columns=['gmap_id', 'name'])
timestamps = pd.to_datetime(reviews['time'].str.strip(), format='mixed', errors='coerce')
if (reviews['time'].notna() & timestamps.isna()).any():
    raise ValueError('Some review timestamps could not be parsed')
qualifying = reviews.loc[timestamps.dt.year.eq(2019) & reviews['rating'].ge(4.5)]
counts = qualifying.groupby('gmap_id').size().rename('high_rating_reviews').reset_index()
ranked = counts.merge(businesses, on='gmap_id', how='left', validate='one_to_one').sort_values(['high_rating_reviews', 'gmap_id'], ascending=[False, True])
assert ranked['name'].notna().all()
ranked.to_csv(OUT / 'ranked_businesses.csv', index=False)
top = ranked.head(3)
answer = '; '.join(f"{row.name}: {row.high_rating_reviews} high-rating reviews" for row in top.itertuples(index=False)) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(top.to_string(index=False))
print(f'Parsed {timestamps.notna().sum()} timestamps; {len(qualifying)} qualifying review rows.')
