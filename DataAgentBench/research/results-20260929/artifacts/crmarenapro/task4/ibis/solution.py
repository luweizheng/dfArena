import json
from pathlib import Path
import ibis

con = ibis.duckdb.connect()
cases = con.read_parquet('/workspace/data/support/Case.parquet')
items = con.read_parquet('/workspace/data/products_orders/OrderItem.parquet')

def clean(expr):
    return expr.strip().re_replace(r'^#+', '')

cases = cases.select(case_id=clean(cases.id), item_id=clean(cases.orderitemid__c), created=cases.createddate.strip().cast('timestamp'))
items = items.select(item_id=clean(items.Id), product_id=clean(items.Product2Id))
items = items.filter(items.product_id == '01tWt000006hVJdIAM')
# Rolling ten-month window relative to the supplied as-of date.
as_of = ibis.timestamp('2021-04-10')
start = as_of - ibis.interval(months=10)
selected = cases.filter((cases.created >= start) & (cases.created < as_of)).semi_join(items, 'item_id')
monthly = selected.group_by(month=selected.created.truncate('M')).aggregate(cases=selected.case_id.nunique())
ranked = monthly.order_by(ibis.desc('cases'), 'month')
rows = ranked.to_pyarrow().to_pylist()
print(rows)
if not rows:
    raise ValueError('No matching cases')
answer = rows[0]['month'].strftime('%B')
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}) + '\n')
