import json
import re
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')

def load(group, table):
    df = pl.read_parquet(ROOT / group / f'{table}.parquet')
    return df.with_columns([
        pl.col(c).str.strip_chars().str.strip_chars_start('#').alias(c)
        for c, dtype in df.schema.items() if dtype == pl.String
    ])

def main():
    task = json.loads(Path('/workspace/task.json').read_text())
    quote_id = re.search(r'Quote Id to be considered is:\s*(\w+)', task['query']).group(1)
    quote = load('sales_pipeline', 'Quote').filter(pl.col('Id') == quote_id)
    assert quote.height == 1
    lines = (load('sales_pipeline', 'QuoteLineItem')
             .filter(pl.col('QuoteId') == quote_id)
             .with_columns(pl.col('Quantity', 'UnitPrice', 'Discount', 'TotalPrice').cast(pl.Float64))
             .join(load('products_orders', 'Product2').select('Id', 'Name'),
                   left_on='Product2Id', right_on='Id'))
    articles = load('support', 'knowledge__kav')
    policy = articles.filter(pl.col('title') == 'Mandatory Bundles for Quotes')
    assert policy.height == 1
    article = policy.row(0, named=True)
    product_names = load('products_orders', 'Product2')['Name'].to_list()
    present = set(lines.filter(pl.col('Quantity') > 0)['Name'].to_list())
    violations = []
    for section in re.split(r'\n\s*\d+\.\s+', article['faq_answer__c'])[1:]:
        heading, body = section.split(':', 1)
        trigger = heading.removesuffix(' Bundle').strip()
        # The first sentence states the mandatory companions; subsequent prose
        # explains benefits rather than adding requirements.
        requirement = body.split('.', 1)[0]
        required = {name for name in product_names if name in requirement} - {trigger}
        if trigger in present and required - present:
            violations.append({'product': trigger, 'missing': sorted(required - present)})
    answer = article['id'] if violations else 'None'
    (OUT / 'evidence.json').write_text(json.dumps({'quote_id': quote_id, 'lines': lines.to_dicts(), 'bundle_violations': violations}, indent=2))
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
    print(json.dumps({'answer': answer}))

if __name__ == '__main__':
    main()
