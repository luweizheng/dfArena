import json
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
con = ibis.duckdb.connect()
def table(group, name):
    return con.read_parquet(str(ROOT / group / f'{name}.parquet'))
def clean(value):
    return value.strip().re_replace('^#', '')

contacts = table('core_crm', 'Contact')
orders = table('products_orders', 'Order')
items = table('products_orders', 'OrderItem')
products = table('products_orders', 'Product2')
contact = contacts.filter(clean(contacts.Id) == '003Wt00000Jqy8SIAR').select(account=clean(contacts.AccountId))
today = ibis.date('2021-07-15')
end = today.truncate('month')
start = end - ibis.interval(months=1)
orders = orders.mutate(account=clean(orders.AccountId), order_id=clean(orders.Id), purchased=orders.EffectiveDate.cast('date'))
relevant = orders.join(contact, 'account').filter(
    (orders.purchased >= start) & (orders.purchased < end),
    orders.Status.strip() == 'Activated',
)
transactions = relevant.join(items, relevant.order_id == clean(items.OrderId)).join(
    products, clean(items.Product2Id) == clean(products.Id)
).select(product_id=clean(products.Id), product_name=products.Name, product_description=products.Description)
# The requested AI unit is identified by its AI product name/description
# within the contact account's completed purchases in the previous month.
result = transactions.filter(
    transactions.product_name.strip().lower().startswith('ai ') |
    transactions.product_description.strip().lower().startswith('ai-driven')
).select(Id=transactions.product_id).distinct()
rows = result.to_pyarrow().to_pylist()
assert len(rows) == 1, f'Expected one matching purchased product, got {rows}'
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': rows[0]['Id']}))
print(json.dumps({'answer': rows[0]['Id']}))
