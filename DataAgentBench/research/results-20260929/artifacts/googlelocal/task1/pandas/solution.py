import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
business = pd.read_parquet(DATA / 'business/business_description.parquet')
reviews = pd.read_parquet(DATA / 'review/review.parquet', columns=['gmap_id', 'rating'])
location = business['description'].str.contains(
    r'\bLos Angeles,\s*(?:CA|California)\b', case=False, na=False, regex=True
)
local = business.loc[location, ['gmap_id', 'name']].drop_duplicates()
means = reviews.groupby('gmap_id', as_index=False)['rating'].mean().rename(
    columns={'rating': 'average_rating'}
)
ranked = local.merge(means, on='gmap_id', how='inner', validate='one_to_one')
ranked = ranked.dropna(subset=['average_rating']).sort_values(
    ['average_rating', 'name', 'gmap_id'], ascending=[False, True, True]
)
ranked.to_csv(OUT / 'ranked_businesses.csv', index=False)
top = ranked.head(5)
answer = '; '.join(
    f"{i}. {row.name} — {row.average_rating:.2f}/5"
    for i, row in enumerate(top.itertuples(index=False), 1)
)
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(ranked.to_string(index=False))
print(answer)
