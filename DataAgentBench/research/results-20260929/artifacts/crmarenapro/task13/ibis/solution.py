import json
from pathlib import Path
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()

def read(group, name):
    return con.read_parquet(str(DATA / group / f'{name}.parquet'))

def clean_id(col):
    return col.strip().re_replace(r'^#+', '')

orders_raw = read('products_orders', 'Order')
items_raw = read('products_orders', 'OrderItem')
users_raw = read('core_crm', 'User')
orders = orders_raw.select(
    order_id=clean_id(orders_raw.Id),
    agent_id=clean_id(orders_raw.OwnerId),
    order_date=orders_raw.EffectiveDate.strip().cast('date'),
)
# Order eligibility uses EffectiveDate; the contract policy applies to opportunities.
today = ibis.date('2022-11-25')
start = today - ibis.interval(months=5)
orders = orders.filter(orders.order_date.between(start, today))
items = items_raw.select(
    order_id=clean_id(items_raw.OrderId),
    amount=items_raw.Quantity.strip().cast('decimal(18,4)')
    * items_raw.UnitPrice.strip().cast('decimal(18,4)'),
)
order_totals = items.group_by('order_id').aggregate(sales=items.amount.sum())
joined = orders.join(order_totals, 'order_id')
agent_totals = joined.group_by('agent_id').aggregate(sales=joined.sales.sum())
users = users_raw.select(agent_id=clean_id(users_raw.Id)).distinct()
ranked = agent_totals.semi_join(users, 'agent_id').order_by(
    ibis.desc('sales'), ibis.asc('agent_id')
)
rows = ranked.to_pyarrow().to_pylist()
if not rows:
    raise RuntimeError('No eligible order sales found')
(OUT / 'answer.json').write_text(json.dumps({'answer': rows[0]['agent_id']}))
print(json.dumps(rows[:5], default=str))
