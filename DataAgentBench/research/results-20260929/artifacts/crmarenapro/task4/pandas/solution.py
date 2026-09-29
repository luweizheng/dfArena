import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
def clean_ids(series):
    return series.astype('string').str.strip().str.lstrip('#')

cases = pd.read_parquet(DATA / 'support/Case.parquet', columns=['id', 'createddate', 'orderitemid__c'])
items = pd.read_parquet(DATA / 'products_orders/OrderItem.parquet', columns=['Id', 'Product2Id'])
for col in ['id', 'orderitemid__c']:
    cases[col] = clean_ids(cases[col])
for col in ['Id', 'Product2Id']:
    items[col] = clean_ids(items[col])
product_items = items.loc[items['Product2Id'].eq('01tWt000006hVJdIAM'), 'Id']
cases = cases.loc[cases['orderitemid__c'].isin(product_items)].copy()
cases['created'] = pd.to_datetime(cases['createddate'].str.strip(), utc=True, format='mixed')
today = pd.Timestamp('2021-04-10', tz='UTC')
start = today - pd.DateOffset(months=10)
window = cases.loc[cases['created'].ge(start) & cases['created'].lt(today + pd.Timedelta(days=1))].copy()
window['month'] = window['created'].dt.tz_localize(None).dt.to_period('M')
counts = window.groupby('month')['id'].nunique().reindex(pd.period_range(start.tz_localize(None), today.tz_localize(None), freq='M'), fill_value=0)
counts.rename('case_count').to_csv(OUT / 'monthly_counts.csv', index_label='month')
print(counts.to_string())
answer = counts.idxmax().strftime('%B')
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
