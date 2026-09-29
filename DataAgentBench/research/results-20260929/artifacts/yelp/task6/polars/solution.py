import json
import re
from datetime import datetime
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
reviews = pl.read_parquet('/workspace/data/user/review.parquet')
formats = ['%Y-%m-%d %H:%M:%S', '%d %b %Y, %H:%M', '%B %d, %Y at %I:%M %p']
reviews = reviews.with_columns(pl.coalesce([pl.col('date').str.to_datetime(f, strict=False) for f in formats]).alias('review_date'))
assert reviews['review_date'].null_count() == 0, 'Unparsed review dates'
ranked = (reviews.filter((pl.col('review_date') >= datetime(2016, 1, 1)) & (pl.col('review_date') < datetime(2016, 7, 1)))
    .group_by('business_ref').agg(pl.len().alias('period_reviews'), pl.col('rating').mean().alias('average_rating'))
    .filter(pl.col('period_reviews') >= 5)
    .with_columns(pl.col('business_ref').str.replace('^businessref_', 'businessid_').alias('business_id'))
    .join(pl.read_parquet('/workspace/data/businessinfo/business.parquet'), on='business_id', how='left', validate='1:1')
    .sort(['average_rating', 'business_id'], descending=[True, False]))
assert ranked.height > 0
winners = ranked.filter(pl.col('average_rating') == pl.col('average_rating').max())
ranked.select('name','period_reviews','average_rating','description').write_json(OUT / 'ranking.json')
print(winners.select('name','period_reviews','average_rating','description').to_dicts())
# The description preserves the business category as a natural-language clause.
answers = []
for row in winners.iter_rows(named=True):
    match = re.search(r"featuring (.*?)(?:, perfect for|\.$)", row['description'])
    assert match, 'Category clause not recognized'
    categories = match.group(1)
    answers.append(f"{row['name']} — {row['average_rating']:g}/5 average from {row['period_reviews']} reviews. Categories: {categories}.")
(OUT / 'answer.json').write_text(json.dumps({'answer': ' '.join(answers)}, ensure_ascii=False) + '\n')
