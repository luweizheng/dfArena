import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
history = pd.read_parquet(DATA / 'support/casehistory__c.parquet')
users = pd.read_parquet(DATA / 'core_crm/User.parquet')

def clean_ids(series):
    return series.astype('string').str.strip().str.lstrip('#')

for col in ['id', 'caseid__c', 'oldvalue__c', 'newvalue__c']:
    history[col] = clean_ids(history[col])
users['Id'] = clean_ids(users['Id'])
history['createddate'] = pd.to_datetime(history['createddate'], utc=True)
# Last four complete calendar quarters before the supplied current date.
today = pd.Timestamp('2023-04-10')
end = today.to_period('Q').start_time.tz_localize('UTC')
start = end - pd.DateOffset(months=12)
assignments = history.loc[history['field__c'].str.strip().eq('Owner Assignment')]
period = assignments.loc[assignments['createddate'].ge(start) & assignments['createddate'].lt(end)]
transfers = period.loc[
    period['oldvalue__c'].isin(users['Id'])
    & period['newvalue__c'].isin(users['Id'])
    & period['oldvalue__c'].ne(period['newvalue__c'])
]
# Both incoming and outgoing owners handled the corresponding case.
handled = pd.concat([
    period[['caseid__c', 'newvalue__c']].rename(columns={'newvalue__c': 'agent'}),
    transfers[['caseid__c', 'oldvalue__c']].rename(columns={'oldvalue__c': 'agent'}),
]).groupby('agent')['caseid__c'].nunique()
counts = transfers.groupby('oldvalue__c').size()
eligible = counts.loc[(counts > 0) & (handled.reindex(counts.index).fillna(0) > 0)]
winners = eligible.loc[eligible.eq(eligible.min())]
assert len(winners) == 1, f'Expected one winner: {winners.to_dict()}'
answer = str(winners.index[0])
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
print(answer)
