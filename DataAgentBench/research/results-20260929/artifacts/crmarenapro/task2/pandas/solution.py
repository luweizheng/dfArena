import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')

def load(group, name):
    frame = pd.read_parquet(ROOT / group / f'{name}.parquet')
    for col in frame.select_dtypes(include='object'):
        frame[col] = frame[col].map(lambda v: v.strip().lstrip('#') if isinstance(v, str) else v)
    return frame

quote_id = '0Q0Wt000001WSDVKA4'
quotes = load('sales_pipeline', 'Quote')
assert quotes['Id'].eq(quote_id).sum() == 1
lines = load('sales_pipeline', 'QuoteLineItem')
lines = lines.loc[lines['QuoteId'].eq(quote_id)].copy()
products = load('products_orders', 'Product2')
items = lines.merge(products[['Id', 'Name']], left_on='Product2Id', right_on='Id', validate='many_to_one')
assert len(items) == len(lines) and len(items) > 0
names = set(items['Name'])
articles = load('support', 'knowledge__kav')
article = articles.loc[articles['title'].eq('Mandatory Bundles for Quotes')].iloc[0]
violations = []
for paragraph in re.split(r'\n\s*\n', article['faq_answer__c']):
    match = re.match(r'\d+\.\s+(.+?) Bundle:', paragraph)
    if not match:
        continue
    primary = match.group(1)
    required = {name for name in products['Name'].dropna().unique() if name != primary and name in paragraph}
    if primary in names and required - names:
        violations.append({'product': primary, 'missing': sorted(required - names)})
answer = article['id'] if violations else 'None'
Path('/workspace/work/evidence.json').write_text(json.dumps(violations, indent=2))
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps({'answer': answer}))

if __name__ == '__main__':
    pass
