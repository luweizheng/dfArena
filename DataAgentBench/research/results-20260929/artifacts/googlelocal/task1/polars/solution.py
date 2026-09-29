import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
businesses = (
    pl.scan_parquet(DATA / 'business/business_description.parquet')
    .filter(pl.col('description').str.contains(r'(?i)\bLos Angeles,\s*(?:CA|California)\b'))
    .select('gmap_id', 'name').unique()
)
ratings = (
    pl.scan_parquet(DATA / 'review/review.parquet')
    .group_by('gmap_id')
    .agg(pl.col('rating').mean().alias('average_rating'), pl.col('rating').count().alias('review_count'))
)
ranked = (
    businesses.join(ratings, on='gmap_id', how='inner')
    .filter(pl.col('average_rating').is_not_null())
    .sort(['average_rating', 'name', 'gmap_id'], descending=[True, False, False])
    .collect()
)
ranked.write_csv(OUT / 'ranked_businesses.csv')
top = ranked.head(5)
answer = '; '.join(
    f"{i}. {row['name']} — {row['average_rating']:.2f}/5"
    for i, row in enumerate(top.iter_rows(named=True), 1)
) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(ranked)
print(answer)
