import json
from datetime import date
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
PRODUCT = '01tWt000006hVJdIAM'
TODAY = date(2021, 4, 10)
START = date(2020, 6, 10)

def clean(name):
    return pl.col(name).str.strip_chars().str.strip_chars_start('#')

cases = pl.read_parquet(DATA / 'support/Case.parquet').with_columns(
    clean('id'), clean('orderitemid__c'),
    pl.col('createddate').str.strip_chars().str.slice(0, 10).str.to_date().alias('created')
)
items = pl.read_parquet(DATA / 'products_orders/OrderItem.parquet').with_columns(
    clean('Id'), clean('Product2Id')
).filter(pl.col('Product2Id') == PRODUCT)
selected = cases.join(items.select('Id'), left_on='orderitemid__c', right_on='Id', how='semi').filter(
    (pl.col('created') >= START) & (pl.col('created') <= TODAY)
)
counts = selected.group_by(pl.col('created').dt.truncate('1mo').alias('month')).agg(
    pl.col('id').n_unique().alias('cases')
).sort('cases', descending=True)
counts.write_csv(OUT / 'monthly_counts.csv')
print(counts)
answer = counts.item(0, 'month').strftime('%B')
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
