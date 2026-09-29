import json
import re
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')

def read_table(group, name):
    df = pl.read_parquet(ROOT / group / (name + '.parquet'))
    return df.with_columns([
        pl.col(c).str.strip_chars().str.strip_prefix('#')
        for c in df.columns if c.lower().endswith('id')
    ])

with open('/workspace/task.json') as f:
    task = json.load(f)
quote_id = re.search(r'0Q0[A-Za-z0-9]+', task['query']).group()
items = read_table('sales_pipeline', 'QuoteLineItem').filter(pl.col('QuoteId') == quote_id)
products = read_table('products_orders', 'Product2').select('Id', pl.col('Name').str.strip_chars())
items = items.join(products, left_on='Product2Id', right_on='Id').with_columns(pl.col('Quantity').cast(pl.Float64))
articles = read_table('support', 'knowledge__kav')
policy = articles.filter(pl.col('title').str.strip_chars() == 'Product Quantity Limits')
limits = []
for article in policy.iter_rows(named=True):
    for name, sentence in re.findall(r'\*\*([^*]+)\*\*\s*-\s*([^.]*)\.', article['faq_answer__c']):
        match = re.search(r'(\d+) units', sentence)
        if match:
            limits.append({'Name': name.strip(), 'limit': float(match.group(1)), 'article_id': article['id']})
violations = items.group_by('Name').agg(pl.col('Quantity').sum()).join(pl.DataFrame(limits), on='Name').filter(pl.col('Quantity') > pl.col('limit'))
ids = violations['article_id'].unique().to_list()
assert len(ids) == 1, f'Expected one quantity policy violation, found {ids}'
violations.write_json('/workspace/work/evidence.json')
with open('/workspace/work/answer.json', 'w') as f:
    json.dump({'answer': ids[0]}, f)
print(json.dumps({'answer': ids[0]}))
