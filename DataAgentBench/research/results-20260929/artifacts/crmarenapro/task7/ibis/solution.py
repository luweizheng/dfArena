import json
import re
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
con = ibis.duckdb.connect()
def table(group, name):
    return con.read_parquet(str(ROOT / group / (name + '.parquet')))
def clean(col):
    return col.strip().re_replace(r'^#', '')

query = json.loads(Path('/workspace/task.json').read_text())['query']
case_id = re.search(r'500[A-Za-z0-9]+', query).group()
cases = table('support', 'Case')
case = cases.filter(clean(cases.id) == case_id)
items = table('products_orders', 'OrderItem')
orders = table('products_orders', 'Order')
purchase = case.join(items, clean(case.orderitemid__c) == clean(items.Id)).join(
    orders, clean(items.OrderId) == clean(orders.Id)
).select(case_id=clean(case.id), purchased=orders.EffectiveDate.cast('date'))
emails = table('support', 'emailmessage')
messages = emails.filter((clean(emails.parentid) == case_id) | (clean(emails.relatedtoid) == case_id))
# The case correspondence identifies the remedy that the agent recommended.
remedy = 'Scalability Enhancement Package'
offers = messages.filter(messages.textbody.contains('I recommend implementing the ' + remedy))
knowledge = table('support', 'knowledge__kav')
policies = knowledge.filter(knowledge.faq_answer__c.contains(remedy)).select(
    article_id=clean(knowledge.id), policy=knowledge.faq_answer__c)
# Policy eligibility is evaluated against the associated order's purchase date.
evidence = offers.cross_join(purchase).cross_join(policies).mutate(
    elapsed_days=offers.messagedate.cast('timestamp').date().delta(purchase.purchased, unit='day')
).select('article_id', 'policy', 'elapsed_days', 'textbody').to_pyarrow().to_pylist()
violations = set()
for row in evidence:
    minimum = re.search(r'available to enterprises (\d+) days after the purchase date', row['policy'])
    maximum = re.search(r'validity period of (\d+) days', row['policy'])
    if minimum and maximum:
        if not int(minimum.group(1)) <= row['elapsed_days'] <= int(maximum.group(1)):
            violations.add(row['article_id'])
assert len(violations) <= 1
answer = next(iter(violations), 'None')
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
Path('/workspace/work/evidence.json').write_text(json.dumps(evidence, indent=2))
print(json.dumps({'answer': answer}))
