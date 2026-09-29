import json
from pathlib import Path
import ibis


def normalize(expr):
    return expr.fill_null('').lower().replace('é', 'e').re_replace('[^a-z0-9]', '')


def main():
    conn = ibis.duckdb.connect()
    tracks = conn.read_parquet('/workspace/data/tracks/tracks.parquet')
    sales = conn.read_parquet('/workspace/data/sales/sales.parquet')
    # Five source representations share song identity: spacing/prefix/suffix
    # variations, Beyonce/Beyoncé, and artist embedded in title when missing.
    # Album variants refer to Sexxxplicit R&B Volume 25; 2007/07/'07 agree.
    title = normalize(tracks.title)
    artist = normalize(tracks.artist)
    matched = tracks.filter(
        title.contains('getmebodied')
        & ((artist == 'beyonce') | title.contains('beyonce'))
    )
    relevant = sales.filter(
        (sales.country == 'Canada') & (sales.store == 'Apple Music')
    ).semi_join(matched, 'track_id')
    result = relevant.aggregate(revenue_usd=relevant.revenue_usd.sum()).to_pyarrow().to_pylist()[0]
    revenue = result['revenue_usd']
    if revenue is None:
        revenue = 0.0
    output = Path('/workspace/work')
    (output / 'answer.json').write_text(json.dumps({'answer': f'${revenue:,.2f} USD'}) + '\n')
    print((output / 'answer.json').read_text(), end='')


if __name__ == '__main__':
    main()
