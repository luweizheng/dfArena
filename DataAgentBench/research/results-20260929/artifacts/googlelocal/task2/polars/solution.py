import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
# Descriptions express massage services as bodywork, soothing treatments,
# body treatments, or rejuvenating treatments and holistic wellness.
pattern = r'(?i)massage|bodywork|soothing treatments|soothing body treatments|rejuvenating treatments and holistic wellness'
businesses = (
    pl.scan_parquet(DATA / 'business/business_description.parquet')
    .filter(pl.col('description').str.contains(pattern))
    .select('gmap_id', 'name', 'description')
    .unique()
)
averages = (
    pl.scan_parquet(DATA / 'review/review.parquet')
    .group_by('gmap_id')
    .agg(pl.col('rating').mean().alias('average_rating'), pl.col('rating').count().alias('review_count'))
)
all_matches = businesses.join(averages, on='gmap_id', how='left').collect()
all_matches.write_csv(OUT / 'massage_business_ratings.csv')
result = all_matches.filter(pl.col('average_rating') >= 4.0).sort('name')
def format_rating(value):
    return f'{value:.4f}'.rstrip('0').rstrip('.') if value % 1 else f'{value:.1f}'
answer = '; '.join(f"{row['name']}: {format_rating(row['average_rating'])}" for row in result.iter_rows(named=True))
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(all_matches.select('name','average_rating','review_count'))
print(answer)

if __name__ == '__main__':
    pass
