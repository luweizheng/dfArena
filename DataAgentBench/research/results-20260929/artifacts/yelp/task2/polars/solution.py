import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
STATE_NAMES = dict(item.split(':', 1) for item in (
    'AL:Alabama|AK:Alaska|AZ:Arizona|AR:Arkansas|CA:California|CO:Colorado|CT:Connecticut|DE:Delaware|FL:Florida|GA:Georgia|HI:Hawaii|ID:Idaho|IL:Illinois|IN:Indiana|IA:Iowa|KS:Kansas|KY:Kentucky|LA:Louisiana|ME:Maine|MD:Maryland|MA:Massachusetts|MI:Michigan|MN:Minnesota|MS:Mississippi|MO:Missouri|MT:Montana|NE:Nebraska|NV:Nevada|NH:New Hampshire|NJ:New Jersey|NM:New Mexico|NY:New York|NC:North Carolina|ND:North Dakota|OH:Ohio|OK:Oklahoma|OR:Oregon|PA:Pennsylvania|RI:Rhode Island|SC:South Carolina|SD:South Dakota|TN:Tennessee|TX:Texas|UT:Utah|VT:Vermont|VA:Virginia|WA:Washington|WV:West Virginia|WI:Wisconsin|WY:Wyoming'
).split('|'))
businesses = pl.read_parquet(DATA / 'businessinfo/business.parquet').select(
    pl.col('business_id').str.replace(r'^businessid_', 'businessref_').alias('business_ref'),
    pl.col('description').str.extract(r', ([A-Z]{2})\b').alias('state'),
)
assert businesses['state'].null_count() == 0
assert businesses['business_ref'].n_unique() == businesses.height
reviews = pl.scan_parquet(DATA / 'user/review.parquet').select('business_ref', 'rating')
summary = (
    reviews.join(businesses.lazy(), on='business_ref', how='inner', validate='m:1')
    .filter(pl.col('state').is_in(list(STATE_NAMES)))
    .group_by('state')
    .agg(pl.len().alias('review_count'), pl.col('rating').mean().alias('average_rating'))
    .sort(['review_count', 'state'], descending=[True, False])
    .collect()
)
summary.write_csv(OUT / 'state_summary.csv')
winners = summary.filter(pl.col('review_count') == summary['review_count'].max())
answer = '; '.join(
    f"{STATE_NAMES[row['state']]} ({row['state']}) has the highest number of reviews ({row['review_count']:,}), with an average rating of {row['average_rating']:.2f} out of 5."
    for row in winners.iter_rows(named=True)
)
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(summary)
print(answer)
