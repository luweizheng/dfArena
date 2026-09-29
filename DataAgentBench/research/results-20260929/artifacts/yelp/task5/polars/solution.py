import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
STATE_NAMES = dict(item.split(':', 1) for item in (
    'AL:Alabama|AK:Alaska|AZ:Arizona|AR:Arkansas|CA:California|CO:Colorado|'
    'CT:Connecticut|DE:Delaware|FL:Florida|GA:Georgia|HI:Hawaii|ID:Idaho|'
    'IL:Illinois|IN:Indiana|IA:Iowa|KS:Kansas|KY:Kentucky|LA:Louisiana|'
    'ME:Maine|MD:Maryland|MA:Massachusetts|MI:Michigan|MN:Minnesota|'
    'MS:Mississippi|MO:Missouri|MT:Montana|NE:Nebraska|NV:Nevada|'
    'NH:New Hampshire|NJ:New Jersey|NM:New Mexico|NY:New York|'
    'NC:North Carolina|ND:North Dakota|OH:Ohio|OK:Oklahoma|OR:Oregon|'
    'PA:Pennsylvania|RI:Rhode Island|SC:South Carolina|SD:South Dakota|'
    'TN:Tennessee|TX:Texas|UT:Utah|VT:Vermont|VA:Virginia|WA:Washington|'
    'WV:West Virginia|WI:Wisconsin|WY:Wyoming'
).split('|'))

businesses = pl.read_parquet(DATA / 'businessinfo/business.parquet').with_columns(
    pl.col('attributes').str.json_path_match('$.WiFi')
      .str.replace(r"^u['\"]", '').str.strip_chars("'\"").alias('wifi'),
    pl.col('description').str.extract(r', ([A-Z]{2})\b', 1).alias('state'),
    pl.col('business_id').str.replace(r'^businessid_', 'businessref_').alias('business_ref'),
)
assert businesses['state'].null_count() == 0
assert businesses['business_id'].n_unique() == businesses.height
# Both free and paid WiFi count as offering WiFi; absent/no values do not.
qualifying = businesses.filter(
    pl.col('wifi').is_in(['free', 'paid']) & pl.col('state').is_in(list(STATE_NAMES))
)
counts = qualifying.group_by('state').agg(pl.len().alias('business_count')).sort(
    ['business_count', 'state'], descending=[True, False]
)
counts.write_csv(OUT / 'wifi_business_counts.csv')
winners = counts.filter(pl.col('business_count') == counts['business_count'].max())
reviews = pl.scan_parquet(DATA / 'user/review.parquet').select('business_ref', 'rating')
results = []
for row in winners.iter_rows(named=True):
    scoped = qualifying.filter(pl.col('state') == row['state']).select('business_ref')
    stats = reviews.join(scoped.lazy(), on='business_ref', how='semi').select(
        pl.len().alias('review_count'), pl.col('rating').mean().alias('average_rating')
    ).collect().row(0, named=True)
    results.append({**row, **stats})
answer = '; '.join(
    f"{STATE_NAMES[r['state']]} ({r['state']}) has the most businesses offering WiFi: "
    f"{r['business_count']}, with an average review rating of {r['average_rating']:.2f}/5."
    for r in results
)
(OUT / 'calculation_details.json').write_text(json.dumps(results, indent=2))
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(counts)
print(json.dumps(results, indent=2))
print(answer)

if __name__ == '__main__':
    pass
