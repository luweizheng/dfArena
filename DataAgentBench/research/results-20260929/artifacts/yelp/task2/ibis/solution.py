import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
b = con.read_parquet('/workspace/data/businessinfo/business.parquet')
r = con.read_parquet('/workspace/data/user/review.parquet')
states = dict(item.split(':') for item in ('AL:Alabama|AK:Alaska|AZ:Arizona|AR:Arkansas|CA:California|CO:Colorado|CT:Connecticut|DE:Delaware|FL:Florida|GA:Georgia|HI:Hawaii|ID:Idaho|IL:Illinois|IN:Indiana|IA:Iowa|KS:Kansas|KY:Kentucky|LA:Louisiana|ME:Maine|MD:Maryland|MA:Massachusetts|MI:Michigan|MN:Minnesota|MS:Mississippi|MO:Missouri|MT:Montana|NE:Nebraska|NV:Nevada|NH:New Hampshire|NJ:New Jersey|NM:New Mexico|NY:New York|NC:North Carolina|ND:North Dakota|OH:Ohio|OK:Oklahoma|OR:Oregon|PA:Pennsylvania|RI:Rhode Island|SC:South Carolina|SD:South Dakota|TN:Tennessee|TX:Texas|UT:Utah|VT:Vermont|VA:Virginia|WA:Washington|WV:West Virginia|WI:Wisconsin|WY:Wyoming').split('|'))
locations = b.select(
    business_ref=b.business_id.re_replace(r'^businessid_', 'businessref_'),
    state=b.description.re_extract(r',\s*([A-Z]{2})\b', 1),
)
# Validate that location parsing and identifier uniqueness cover the source.
assert locations.business_ref.nunique().execute() == b.count().execute()
missing = locations.filter(locations.state.isnull() | (locations.state == '')).count().execute()
assert missing == 0, f'{missing} descriptions lack a parsed state'
joined = r.join(locations, 'business_ref')
assert joined.count().execute() == r.count().execute()
us_reviews = joined.filter(joined.state.isin(list(states)))
summary = us_reviews.group_by('state').aggregate(
    review_count=us_reviews.count(),
    average_rating=us_reviews.rating.mean(),
).order_by(ibis.desc('review_count'), 'state')
rows = summary.to_pyarrow().to_pylist()
(OUT / 'state_summary.json').write_text(json.dumps(rows, indent=2))
top = rows[0]
winners = [row for row in rows if row['review_count'] == top['review_count']]
answer = '; '.join(f"{states[row['state']]} ({row['state']}) has the highest number of reviews ({row['review_count']:,}), with an average rating of {row['average_rating']:.2f} out of 5." for row in winners)
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(answer)
