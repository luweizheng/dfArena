import json
import re
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()

def table(group, name):
    return con.read_parquet(str(ROOT / group / (name + '.parquet')))

def clean_id(col):
    return col.strip().re_replace(r'^#', '')

quote = table('sales_pipeline', 'Quote')
lines = table('sales_pipeline', 'QuoteLineItem')
products = table('products_orders', 'Product2')
articles = table('support', 'knowledge__kav')
selected = quote.filter(clean_id(quote.Id) == '0Q0Wt000001WSDVKA4')
selected_lines = lines.join(selected, clean_id(lines.QuoteId) == clean_id(selected.Id)).select(lines)
items = selected_lines.join(products, clean_id(selected_lines.Product2Id) == clean_id(products.Id)).select(
    product=products.Name.strip(), quantity=selected_lines.Quantity.cast('float64'),
    unit_price=selected_lines.UnitPrice.cast('float64'), discount=selected_lines.Discount.cast('float64'))
item_rows = items.to_pyarrow().to_pylist()
names = {row['product'] for row in item_rows}
policy_rows = articles.filter(articles.title.strip() == 'Mandatory Bundles for Quotes').select(
    article_id=clean_id(articles.id), text=articles.faq_answer__c).to_pyarrow().to_pylist()
violations = []
evidence = []
for policy in policy_rows:
    for block in re.split(r'\n\s*\n', policy['text']):
        match = re.match(r'\d+\. ([^:]+) Bundle:', block)
        if not match or match.group(1) not in names:
            continue
        # The first sentence of each numbered rule specifies its companions.
        sentence = block.split(':', 1)[1].split('.', 1)[0]
        catalog = products.filter(products.Name.strip() != match.group(1)).select(name=products.Name.strip()).distinct().to_pyarrow().to_pylist()
        required = {r['name'] for r in catalog if r['name'] in sentence}
        missing = required - names
        if missing:
            violations.append(policy['article_id'])
            evidence.append({'product': match.group(1), 'missing': sorted(missing), 'article_id': policy['article_id']})
assert len(set(violations)) <= 1
answer = violations[0] if violations else 'None'
(OUT / 'evidence.json').write_text(json.dumps({'items': item_rows, 'violations': evidence}, indent=2))
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
