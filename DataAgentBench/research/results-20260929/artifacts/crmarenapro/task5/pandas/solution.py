import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
PRODUCT_ID = '01tWt000006hV8LIAU'
TODAY = pd.Timestamp('2023-01-16', tz='UTC')
START = TODAY - pd.DateOffset(months=5)

def clean_id(series):
    return series.astype('string').str.strip().str.lstrip('#')

cases = pd.read_parquet(DATA / 'support/Case.parquet', columns=['id', 'createddate', 'orderitemid__c', 'issueid__c'])
items = pd.read_parquet(DATA / 'products_orders/OrderItem.parquet', columns=['Id', 'Product2Id'])
for col in ['id', 'orderitemid__c', 'issueid__c']:
    cases[col] = clean_id(cases[col])
for col in ['Id', 'Product2Id']:
    items[col] = clean_id(items[col])
product_items = items.loc[items['Product2Id'].eq(PRODUCT_ID), 'Id']
created = pd.to_datetime(cases['createddate'].str.strip(), utc=True)
# Include the as-of date in full; the lower bound is five calendar months earlier.
selected = cases.loc[cases['orderitemid__c'].isin(product_items) & created.ge(START) & created.lt(TODAY + pd.Timedelta(days=1))]
counts = selected.loc[selected['issueid__c'].notna() & selected['issueid__c'].ne('')].groupby('issueid__c').size().sort_values(ascending=False)
assert not counts.empty, 'No matching issues'
assert counts.eq(counts.iloc[0]).sum() == 1, 'Most frequent issue is tied'
counts.rename('case_count').to_csv(OUT / 'issue_counts.csv')
answer = str(counts.index[0])
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(counts.to_string())
print(json.dumps({'answer': answer}))
