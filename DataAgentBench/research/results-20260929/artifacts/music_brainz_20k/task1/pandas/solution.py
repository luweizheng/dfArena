import json
import re
import unicodedata
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def normalize(value):
    if pd.isna(value):
        return ''
    value = unicodedata.normalize('NFKD', str(value)).casefold()
    return re.sub(r'[^a-z0-9]', '', value)

tracks = pd.read_parquet(DATA / 'tracks/tracks.parquet')
sales = pd.read_parquet(DATA / 'sales/sales.parquet')
titles = tracks['title'].map(normalize)
artists = tracks['artist'].map(normalize)
# Resolve song-level duplicates, including compilation suffixes, track-number
# prefixes, missing spaces, accent variants, and an artist embedded in title.
matched = tracks[
    titles.str.contains(normalize('Get Me Bodied'), regex=False)
    & (artists.eq(normalize('Beyoncé'))
       | titles.str.contains(normalize('Beyoncé'), regex=False))
]
assert not matched.empty
assert tracks['track_id'].is_unique
selected = sales[
    sales['track_id'].isin(matched['track_id'])
    & sales['country'].map(normalize).eq(normalize('Canada'))
    & sales['store'].map(normalize).eq(normalize('Apple Music'))
]
assert selected['revenue_usd'].notna().all()
revenue = selected['revenue_usd'].sum()
matched.to_csv(OUT / 'matched_tracks.csv', index=False)
selected.to_csv(OUT / 'matched_sales.csv', index=False)
answer = {'answer': f'${revenue:,.2f} USD'}
(OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
print(f'Matched tracks: {len(matched)}; sales: {len(selected)}')
print(json.dumps(answer))
