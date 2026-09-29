import json
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
reviews = pl.read_parquet('/workspace/data/review/review.parquet')
businesses = pl.read_parquet('/workspace/data/business/business_description.parquet')
formats = ['%Y-%m-%d %H:%M:%S', '%B %d, %Y at %I:%M %p', '%d %b %Y, %H:%M']
reviews = reviews.with_columns(pl.coalesce([
    pl.col('time').str.strptime(pl.Datetime, fmt, strict=False) for fmt in formats
]).alias('review_time'))
assert reviews['review_time'].null_count() == 0, 'Unparsed review timestamps'
assert businesses['gmap_id'].n_unique() == businesses.height
counts = (reviews.filter((pl.col('review_time').dt.year() == 2019) & (pl.col('rating') >= 4.5))
          .group_by('gmap_id').agg(pl.len().alias('high_rating_reviews')))
ranked = (counts.join(businesses.select('gmap_id', 'name'), on='gmap_id', how='left', validate='1:1')
          .sort(['high_rating_reviews', 'name', 'gmap_id'], descending=[True, False, False]))
assert ranked['name'].null_count() == 0
ranked.write_csv(OUT / 'ranked_businesses.csv')
top = ranked.head(3)
answer = '; '.join(f"{row['name']}: {row['high_rating_reviews']} high-rating reviews" for row in top.iter_rows(named=True)) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(top)
print(answer)
