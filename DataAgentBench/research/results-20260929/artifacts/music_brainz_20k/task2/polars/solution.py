import json
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
tracks = pl.read_parquet('/workspace/data/tracks/tracks.parquet')
sales = pl.read_parquet('/workspace/data/sales/sales.parquet')

def normalized(column):
    return pl.col(column).fill_null('').str.to_lowercase().str.replace_all(r'[^a-z0-9]', '')

# Source formats add artist/album text and track numbers to titles.
# Normalize whitespace and punctuation, and accept the observed doubled t.
# Artist identity may be embedded in the title when artist is missing.
resolved = tracks.with_columns(
    normalized('title').alias('_title'),
    normalized('artist').alias('_artist'),
    normalized('album').alias('_album'),
).filter(
    pl.col('_title').str.contains(r'st+reethype')
    & (pl.col('_artist').str.contains('maginnis') | pl.col('_title').str.contains('maginnis'))
    & (pl.col('_album').str.contains('groovecity') | pl.col('_title').str.contains('groovecity'))
)
# Supporting metadata: 2005/'05/05 and 177 seconds, 177000 ms,
# 2.95 minutes, 2m 57sec, or 02:57 (misplaced in language).
assert resolved.height > 0
resolved.write_csv(OUT / 'resolved_tracks.csv')
totals = (
    sales.join(resolved.select('track_id'), on='track_id', how='semi')
    .group_by('store')
    .agg(pl.col('revenue_usd').sum().alias('revenue_usd'))
    .sort('revenue_usd', descending=True)
)
totals.write_csv(OUT / 'store_revenue.csv')
winner = totals.row(0, named=True)
answer = f"{winner['store']} earned the most revenue: ${winner['revenue_usd']:,.2f} USD."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(totals)
print(answer)
