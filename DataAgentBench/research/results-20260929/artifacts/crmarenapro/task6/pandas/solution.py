import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
def clean(series):
    return series.astype('string').str.strip().str.lstrip('#')

def main():
    task = json.loads(Path('/workspace/task.json').read_text())
    quote_id = re.search(r'Quote Id to be considered is:\s*(\w+)', task['query']).group(1)
    lines = pd.read_parquet(DATA / 'sales_pipeline/QuoteLineItem.parquet')
    products = pd.read_parquet(DATA / 'products_orders/Product2.parquet')
    articles = pd.read_parquet(DATA / 'support/knowledge__kav.parquet')
    lines = lines.loc[clean(lines['QuoteId']).eq(quote_id)].copy()
    lines['product_key'] = clean(lines['Product2Id'])
    products['product_key'] = clean(products['Id'])
    products['Name'] = products['Name'].str.strip()
    lines = lines.merge(products[['product_key', 'Name']], on='product_key', validate='many_to_one')
    lines['Quantity'] = pd.to_numeric(lines['Quantity'])
    quantities = lines.groupby('Name')['Quantity'].sum()
    violations = []
    evidence = []
    for _, article in articles.iterrows():
        if article['title'].strip() != 'Product Quantity Limits':
            continue
        for name, paragraph in re.findall(r'\*\*(.*?)\*\*\s*-\s*(.*?)(?=\n\n|$)', article['faq_answer__c'], re.S):
            match = re.search(r'(\d+) units', paragraph)
            if match and name in quantities.index:
                limit = int(match.group(1))
                quantity = float(quantities[name])
                if quantity > limit:
                    violations.append(article['id'].strip().lstrip('#'))
                    evidence.append({'product': name, 'quantity': quantity, 'limit': limit})
    violations = list(dict.fromkeys(violations))
    assert len(violations) == 1, violations
    (OUT / 'evidence.json').write_text(json.dumps(evidence, indent=2))
    (OUT / 'answer.json').write_text(json.dumps({'answer': violations[0]}))

if __name__ == '__main__':
    main()
