import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
today = pd.Timestamp('2022-10-26', tz='UTC')
# Past six quarters means the six completed calendar quarters.
end = today.tz_localize(None).to_period('Q').start_time.tz_localize('UTC')
start = end - pd.DateOffset(months=18)
cases = pd.read_parquet(DATA / 'support/Case.parquet')
accounts = pd.read_parquet(DATA / 'core_crm/Account.parquet', columns=['Id', 'ShippingState'])

def clean_id(s):
    return s.astype('string').str.strip().str.lstrip('#')

cases['accountid'] = clean_id(cases['accountid'])
accounts['Id'] = clean_id(accounts['Id'])
accounts['ShippingState'] = accounts['ShippingState'].str.strip()
cases['status'] = cases['status'].str.strip()
for column in ['createddate', 'closeddate']:
    cases[column] = pd.to_datetime(cases[column].str.strip(), utc=True, errors='coerce')
joined = cases.merge(accounts, left_on='accountid', right_on='Id', how='left', validate='many_to_one')
# Compare cases closed during the reporting period, with equal case weights.
selected = joined.loc[
    joined['status'].eq('Closed')
    & joined['closeddate'].ge(start)
    & joined['closeddate'].lt(end)
    & joined['createddate'].notna()
].copy()
selected['closure_seconds'] = (selected['closeddate'] - selected['createddate']).dt.total_seconds()
assert selected['closure_seconds'].ge(0).all()
assert selected['ShippingState'].notna().all()
ranking = selected.groupby('ShippingState')['closure_seconds'].agg(['mean', 'count']).sort_values('mean')
assert not ranking.empty
ranking.to_csv(OUT / 'state_closure_times.csv')
answer = str(ranking.index[0])
assert len(answer) == 2
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(f'Period: {start} to {end} (exclusive)')
print(ranking.to_string())
