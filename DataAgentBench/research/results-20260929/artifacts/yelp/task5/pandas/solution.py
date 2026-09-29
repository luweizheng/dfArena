import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
STATES = dict(item.split(':') for item in 'AL:Alabama|AK:Alaska|AZ:Arizona|AR:Arkansas|CA:California|CO:Colorado|CT:Connecticut|DE:Delaware|FL:Florida|GA:Georgia|HI:Hawaii|ID:Idaho|IL:Illinois|IN:Indiana|IA:Iowa|KS:Kansas|KY:Kentucky|LA:Louisiana|ME:Maine|MD:Maryland|MA:Massachusetts|MI:Michigan|MN:Minnesota|MS:Mississippi|MO:Missouri|MT:Montana|NE:Nebraska|NV:Nevada|NH:New Hampshire|NJ:New Jersey|NM:New Mexico|NY:New York|NC:North Carolina|ND:North Dakota|OH:Ohio|OK:Oklahoma|OR:Oregon|PA:Pennsylvania|RI:Rhode Island|SC:South Carolina|SD:South Dakota|TN:Tennessee|TX:Texas|UT:Utah|VT:Vermont|VA:Virginia|WA:Washington|WV:West Virginia|WI:Wisconsin|WY:Wyoming'.split('|'))

def wifi_value(cell):
    if pd.isna(cell):
        return None
    value = json.loads(cell).get('WiFi', '')
    # Normalize literal quote wrappers without executing attribute strings.
    if value.startswith(('u\"', "u'")):
        value = value[1:]
    return value.strip("'\"").lower()

business = pd.read_parquet(DATA / 'businessinfo/business.parquet')
business['state'] = business.description.str.extract(r',\s*([A-Z]{2})\b', expand=False)
assert business.state.notna().all(), 'Unparsed business location'
business['wifi'] = business.attributes.map(wifi_value)
qualifying = business.loc[business.wifi.isin(['free', 'paid']) & business.state.isin(STATES)].copy()
counts = qualifying.groupby('state').business_id.nunique().sort_values(ascending=False)
reviews = pd.read_parquet(DATA / 'user/review.parquet', columns=['business_ref', 'rating'])
qualifying['business_ref'] = qualifying.business_id.str.replace(r'^businessid_', 'businessref_', regex=True)
results = []
for state in counts[counts.eq(counts.max())].index:
    refs = qualifying.loc[qualifying.state.eq(state), 'business_ref']
    ratings = reviews.loc[reviews.business_ref.isin(refs), 'rating']
    assert len(ratings) > 0
    results.append(f'{STATES[state]} ({state}) has {int(counts[state])} businesses offering WiFi; their average review rating is {ratings.mean():.2f} out of 5.')
    print(state, 'businesses:', counts[state], 'reviews:', len(ratings), 'rating sum:', ratings.sum(), 'average:', ratings.mean())
counts.to_csv(OUT / 'wifi_business_counts.csv')
(OUT / 'answer.json').write_text(json.dumps({'answer': ' '.join(results)}) + '\n')
print(counts.to_string())
