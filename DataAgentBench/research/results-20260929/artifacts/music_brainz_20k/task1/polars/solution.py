import json
import re
import unicodedata
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')

def normalize(value):
    value = unicodedata.normalize('NFKD', value or '')
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in value if not unicodedata.combining(c)).lower())

tracks = pl.read_parquet('/workspace/data/tracks/tracks.parquet')
# These records share the song title and artist (sometimes embedded in title).
# Album annotations, track-number prefixes, and year formats vary by source.
resolved = tracks.with_columns(
    pl.col('title').map_elements(normalize, return_dtype=pl.String).alias('title_key'),
    pl.col('artist').fill_null('').map_elements(normalize, return_dtype=pl.String).alias('artist_key'),
).filter(
    pl.col('title_key').str.contains('getmebodied')
    & ((pl.col('artist_key') == 'beyonce') | pl.col('title_key').str.contains('beyonce'))
)
assert resolved.height > 0
sales = pl.read_parquet('/workspace/data/sales/sales.parquet')
selected = sales.filter(
    (pl.col('country') == 'Canada') & (pl.col('store') == 'Apple Music')
).join(resolved.select('track_id'), on='track_id', how='semi')
# Sum in decimal dollars to avoid binary floating-point rounding artifacts.
total = selected.select(pl.col('revenue_usd').cast(pl.Decimal(precision=24, scale=2)).sum()).item()
resolved.write_csv(OUT / 'resolved_tracks.csv')
selected.write_csv(OUT / 'selected_sales.csv')
answer = {'answer': f'${total:,.2f} USD'}
(OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
print(f'Matched tracks: {resolved.height}; sales: {selected.height}')
print(json.dumps(answer))
