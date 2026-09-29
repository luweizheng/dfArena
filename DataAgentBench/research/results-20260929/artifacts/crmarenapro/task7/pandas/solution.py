import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')
def load(group, table):
    return pd.read_parquet(ROOT / group / (table + '.parquet'))
def clean(series):
    return series.astype('string').str.strip().str.lstrip('#')

task = json.loads(Path('/workspace/task.json').read_text())
case_id = re.search(r'Case Id to be considered is:\s*(\w+)', task['query']).group(1)
cases = load('support', 'Case')
case = cases.loc[clean(cases.id).eq(case_id)].iloc[0]
items = load('products_orders', 'OrderItem')
item = items.loc[clean(items.Id).eq(str(case.orderitemid__c).strip().lstrip('#'))].iloc[0]
orders = load('products_orders', 'Order')
order = orders.loc[clean(orders.Id).eq(str(item.OrderId).strip().lstrip('#'))].iloc[0]
emails = load('support', 'emailmessage')
emails = emails.loc[clean(emails.parentid).eq(case_id)].copy()
articles = load('support', 'knowledge__kav')
# Identify the offered remedy from the conversation, then retrieve its policy.
remedy = 'Scalability Enhancement Package'
offers = emails.loc[emails.textbody.str.contains('I recommend implementing the ' + remedy, case=False, na=False)]
matching = articles.loc[articles.faq_answer__c.str.contains(remedy, regex=False, na=False)]
violations = []
for _, article in matching.iterrows():
    policy = article.faq_answer__c
    wait = re.search(r'(\d+) days after the purchase date', policy)
    validity = re.search(r'validity period of (\d+) days', policy)
    if wait is None or validity is None:
        continue
    purchase = pd.to_datetime(order.EffectiveDate, utc=True)
    for _, offer in offers.iterrows():
        age = (pd.to_datetime(offer.messagedate, utc=True) - purchase).days
        if age < int(wait.group(1)) or age > int(validity.group(1)):
            violations.append(str(article.id).strip().lstrip('#'))
answer = next(iter(dict.fromkeys(violations)), 'None')
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))

if __name__ == '__main__':
    print(answer)
