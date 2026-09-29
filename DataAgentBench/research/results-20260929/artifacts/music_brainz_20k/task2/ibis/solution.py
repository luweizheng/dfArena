import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
tracks = con.read_parquet('/workspace/data/tracks/tracks.parquet')
sales = con.read_parquet('/workspace/data/sales/sales.parquet')

def normalized(expr):
    return expr.fill_null('').lower().re_replace('[^a-z0-9]', '')

# Resolve source-specific title decorations, whitespace corruption, and
# the observed doubled-t typo. Artist can be embedded in the source title.
# Album appears either in its own column or appended to the track title.
# Matching records consistently describe Groove City (2005), 177 seconds:
# 177000 ms, 2.95 minutes, 2m 57sec, or 02:57 in the shifted language field.
title = normalized(tracks.title).replace('sttreet', 'street')
artist = normalized(tracks.artist)
album = normalized(tracks.album)
matched = tracks.filter(
    title.contains('streethype')
    & (artist.contains('maginnis') | title.contains('maginnis'))
    & (album.contains('groovecity') | title.contains('groovecity'))
)
joined = sales.inner_join(matched.select('track_id'), 'track_id')
ranking = joined.group_by('store').aggregate(
    total_revenue_usd=joined.revenue_usd.sum()
).order_by(ibis.desc('total_revenue_usd'), 'store')
rows = ranking.to_pyarrow().to_pylist()
assert rows, 'No matching sales'
OUT.joinpath('matched_tracks.json').write_text(json.dumps(matched.to_pyarrow().to_pylist(), indent=2))
OUT.joinpath('store_totals.json').write_text(json.dumps(rows, indent=2))
winner = rows[0]
answer = f"{winner['store']} earned the most revenue: ${winner['total_revenue_usd']:,.2f} USD."
OUT.joinpath('answer.json').write_text(json.dumps({'answer': answer}))
print(answer)
print(json.dumps(rows, indent=2))
