import json
import re
from datetime import date, timedelta
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
task = json.loads(Path('/workspace/task.json').read_text())
contact_id = re.search(r'Contact Id interacting:\s*(\S+)', task['query']).group(1)
today = date.fromisoformat(re.search(r"Today's date:\s*(\d{4}-\d{2}-\d{2})", task['query']).group(1))
end = today.replace(day=1)
start = (end - timedelta(days=1)).replace(day=1)

def read(group, table):
    df = pl.read_parquet(ROOT / group / f'{table}.parquet')
    expressions = []
    for col, dtype in df.schema.items():
        if dtype == pl.String:
            expr = pl.col(col).str.strip_chars()
            if col == 'Id' or col.endswith('Id'):
                expr = expr.str.strip_prefix('#')
            expressions.append(expr.alias(col))
    return df.with_columns(expressions)

contacts = read('core_crm', 'Contact').filter(pl.col('Id') == contact_id)
orders = read('products_orders', 'Order').with_columns(pl.col('EffectiveDate').str.to_date())
orders = orders.join(contacts.select('AccountId').unique(), on='AccountId', how='semi').filter(
    (pl.col('EffectiveDate') >= start) & (pl.col('EffectiveDate') < end) & (pl.col('Status') == 'Activated')
)
items = read('products_orders', 'OrderItem').join(orders.select(pl.col('Id').alias('OrderId')), on='OrderId')
products = read('products_orders', 'Product2')
transactions = items.join(products, left_on='Product2Id', right_on='Id')
matched = transactions.filter(pl.concat_str(['Name', 'Description'], separator=' ').str.contains(r'(?i)\bAI\b|artificial intelligence'))
ids = matched['Product2Id'].unique().to_list()
assert len(ids) == 1, f'Expected one matching product, found {ids}'
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': ids[0]}))
print(json.dumps({'answer': ids[0]}))
