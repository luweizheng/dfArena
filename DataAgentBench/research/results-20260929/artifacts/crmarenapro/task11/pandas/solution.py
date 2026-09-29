import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')

def load(group, table):
    frame = pd.read_parquet(DATA / group / f'{table}.parquet')
    for column in frame.select_dtypes(include='object'):
        frame[column] = frame[column].str.strip()
        if column.lower().endswith('id'):
            frame[column] = frame[column].str.lstrip('#')
    return frame

contacts = load('core_crm', 'Contact')
orders = load('products_orders', 'Order')
items = load('products_orders', 'OrderItem')
products = load('products_orders', 'Product2')
contact_id = '003Wt00000Jqy8SIAR'
today = pd.Timestamp('2021-07-15')
end = today.replace(day=1)
start = end - pd.DateOffset(months=1)
accounts = contacts.loc[contacts.Id.eq(contact_id), 'AccountId']
dates = pd.to_datetime(orders.EffectiveDate)
relevant = orders.loc[orders.AccountId.isin(accounts) & dates.ge(start) & dates.lt(end) & orders.Status.eq('Activated')]
purchased = items.loc[items.OrderId.isin(relevant.Id)].merge(products, left_on='Product2Id', right_on='Id', validate='many_to_one')
ai_match = (purchased.Name.str.contains(r'\bAI\b', case=False, na=False) | purchased.Description.str.contains(r'\bAI[- ]', case=False, na=False))
ids = purchased.loc[ai_match, 'Product2Id'].drop_duplicates()
assert len(ids) == 1, f'Expected one matching product, found {len(ids)}'
answer = {'answer': ids.iloc[0]}
Path('/workspace/work/answer.json').write_text(json.dumps(answer))
print(json.dumps(answer))
