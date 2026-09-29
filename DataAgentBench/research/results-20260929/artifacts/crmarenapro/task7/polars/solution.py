import json
import re
from datetime import date
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
CASE_ID = '500Wt00000DDyznIAD'
def norm(c):
    return pl.col(c).str.strip_chars().str.strip_chars_start('#')
def table(group, name):
    return pl.read_parquet(DATA / group / (name + '.parquet'))
case = table('support', 'Case').filter(norm('id') == CASE_ID).row(0, named=True)
item = table('products_orders', 'OrderItem').filter(norm('Id') == case['orderitemid__c'].strip().lstrip('#')).row(0, named=True)
order = table('products_orders', 'Order').filter(norm('Id') == item['OrderId'].strip().lstrip('#')).row(0, named=True)
articles = table('support', 'knowledge__kav')
article = articles.filter(pl.col('faq_answer__c').str.contains('Scalability Enhancement Package')).row(0, named=True)
policy = article['faq_answer__c']
minimum = int(re.search(r'(\d+) days after the purchase date', policy).group(1))
validity = int(re.search(r'validity period of (\d+) days', policy).group(1))
emails = table('support', 'emailmessage').filter((norm('parentid') == CASE_ID) | (norm('relatedtoid') == CASE_ID))
# Identify the agent's offer rather than the customer's subsequent inquiry.
offers = emails.filter(pl.col('textbody').str.contains('I recommend implementing the Scalability Enhancement Package'))
purchase = date.fromisoformat(order['EffectiveDate'][:10])
violations = []
for email in offers.iter_rows(named=True):
    elapsed = (date.fromisoformat(email['messagedate'][:10]) - purchase).days
    if elapsed < minimum or elapsed > validity:
        violations.append({'email_id': email['id'], 'elapsed_days': elapsed})
answer = article['id'].strip().lstrip('#') if violations else 'None'
(OUT / 'evidence.json').write_text(json.dumps({'purchase_date': str(purchase), 'minimum_days': minimum, 'validity_days': validity, 'violations': violations}, indent=2))
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps({'answer': answer}))
