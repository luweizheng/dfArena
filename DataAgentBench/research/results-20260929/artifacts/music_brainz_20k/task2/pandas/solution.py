import json
import re
from difflib import SequenceMatcher
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace')
tracks = pd.read_parquet(ROOT / 'data/tracks/tracks.parquet')
sales = pd.read_parquet(ROOT / 'data/sales/sales.parquet')

def compact(value):
    return re.sub(r'[^a-z0-9]', '', str(value).lower())

def base_title(value):
    value = re.sub(r'^\s*\d+\s*-\s*', '', str(value))
    value = re.split(r'\s+-\s+|\s*\(', value)[0]
    return compact(value)

seed = tracks.loc[
    tracks['title'].map(compact).eq(compact('Street Hype'))
    & tracks['artist'].map(compact).eq(compact('Brucqe Maginnis'))
].iloc[0]
# Match title after removing source-specific album suffixes and track numbers.
# Allow the minor artist typo, while requiring corroborating album information.
artist_match = tracks['artist'].map(
    lambda x: SequenceMatcher(None, compact(x), compact(seed['artist'])).ratio() >= 0.85
)
album_match = tracks.apply(
    lambda row: compact(seed['album']) in compact(row['album'])
    or compact(seed['album']) in compact(row['title']), axis=1
)
matched = tracks.loc[
    tracks['title'].map(base_title).eq(base_title(seed['title']))
    & artist_match & album_match
]
matched.to_csv(ROOT / 'work/matched_tracks.csv', index=False)
revenue = (sales.loc[sales['track_id'].isin(matched['track_id'])]
           .groupby('store')['revenue_usd'].sum().sort_values(ascending=False))
assert not revenue.empty
revenue.to_csv(ROOT / 'work/revenue_by_store.csv')
answer = f'{revenue.index[0]} (${revenue.iloc[0]:,.2f} USD).'
(ROOT / 'work/answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(matched.to_string(index=False))
print(revenue.to_string())
print(answer)
