import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def clean(series):
    return series.astype('string').str.strip().str.lstrip('#')

cases = pd.read_parquet(DATA / 'support/Case.parquet')
history = pd.read_parquet(DATA / 'support/casehistory__c.parquet')
for col in ['id', 'ownerid']:
    cases[col] = clean(cases[col])
for col in ['id', 'caseid__c', 'oldvalue__c', 'newvalue__c']:
    history[col] = clean(history[col])
for col in ['createddate', 'closeddate']:
    cases[col] = pd.to_datetime(cases[col], utc=True)

# Four calendar months preceding the supplied current date.
today = pd.Timestamp('2023-09-02', tz='UTC')
start = today - pd.DateOffset(months=4)
recent = cases.loc[cases.createddate.ge(start) & cases.createddate.lt(today)].copy()
assignments = history.loc[history.field__c.str.strip().eq('Owner Assignment')]
assignment_count = assignments.groupby('caseid__c').size()

# Every assigned agent receives credit for eligibility, including open cases.
handled = assignments.loc[assignments.caseid__c.isin(recent.id), ['caseid__c', 'newvalue__c']].rename(columns={'caseid__c': 'id', 'newvalue__c': 'agent'})
handled = pd.concat([handled, recent[['id','ownerid']].rename(columns={'ownerid':'agent'})]).dropna().drop_duplicates()
counts = handled.groupby('agent').id.nunique()
eligible = counts.index[counts.gt(1)]
closed = recent.loc[recent.closeddate.notna() & recent.closeddate.lt(today) & recent.id.map(assignment_count).eq(1)].copy()
closed['handle_seconds'] = (closed.closeddate - closed.createddate).dt.total_seconds()
means = closed.loc[closed.ownerid.isin(eligible)].groupby('ownerid').handle_seconds.mean().sort_values()
assert not means.empty
means.to_csv(OUT / 'agent_average_handle_seconds.csv')
answer = str(means.index[0])
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(means.to_string())
