import json
import re
from pathlib import Path
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()

def table(group, name):
    return con.read_parquet(str(DATA / group / (name + '.parquet')))

def clean_id(col):
    return col.strip().re_replace(r'^#', '')

lines = table('sales_pipeline', 'QuoteLineItem')
products = table('products_orders', 'Product2')
articles = table('support', 'knowledge__kav')
quote_lines = lines.filter(clean_id(lines.QuoteId) == '0Q0Wt000001WRAzKAO')
quantities = quote_lines.join(products, clean_id(quote_lines.Product2Id) == clean_id(products.Id)).select(
    product=products.Name.strip(), quantity=quote_lines.Quantity.cast('float64')
).group_by('product').aggregate(quantity=lambda t: t.quantity.sum())

# Interpret the quantity restrictions from the policy's natural-language text.
policies = articles.filter(articles.title.strip() == 'Product Quantity Limits').select(
    article_id=clean_id(articles.id), body=articles.faq_answer__c
).to_pyarrow().to_pylist()
rules = []
for policy in policies:
    for name, paragraph in re.findall(r'\*\*([^*]+)\*\*\s*-\s*(.*?)(?=\n\n|$)', policy['body'], re.S):
        limit = re.search(r'(\d+) units', paragraph)
        if limit:
            rules.append({'product': name.strip(), 'limit': float(limit.group(1)), 'article_id': policy['article_id']})
assert rules, 'No quantity restrictions found'
limits = ibis.memtable(rules)
compared = quantities.join(limits, 'product')
violations = compared.filter(compared.quantity > compared['limit'])
results = violations.select('article_id').distinct().to_pyarrow().to_pylist()
assert len(results) == 1, f'Expected one quantity policy violation: {results}'
(OUT / 'answer.json').write_text(json.dumps({'answer': results[0]['article_id']}))

if __name__ == '__main__':
    print(json.dumps({'answer': results[0]['article_id']}))
