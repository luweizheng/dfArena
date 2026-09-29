import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
STATES = dict(item.split(':', 1) for item in (
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

business = pd.read_parquet(DATA / 'businessinfo/business.parquet', columns=['business_id', 'description'])
review = pd.read_parquet(DATA / 'user/review.parquet', columns=['business_ref', 'rating'])
business['state'] = business['description'].str.extract(r',\s*([A-Z]{2})\b', expand=False)
assert business['state'].notna().all(), 'Unparsed business locations'
business['business_ref'] = business['business_id'].str.replace(r'^businessid_', 'businessref_', regex=True)
joined = review.merge(business[['business_ref', 'state']], on='business_ref', how='left', validate='many_to_one', indicator=True)
assert joined['_merge'].eq('both').all(), 'Unmatched reviews'
summary = (joined[joined['state'].isin(STATES)].groupby('state')
           .agg(review_count=('rating', 'size'), average_rating=('rating', 'mean'))
           .sort_values('review_count', ascending=False))
summary.to_csv(OUT / 'state_summary.csv')
winners = summary[summary['review_count'].eq(summary['review_count'].max())]
answer = '; '.join(f'{STATES[state]} ({state}) has {int(row.review_count):,} reviews, with an average rating of {row.average_rating:.2f} out of 5.' for state, row in winners.iterrows())
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(summary.to_string())
print(answer)

if __name__ == '__main__':
    pass
