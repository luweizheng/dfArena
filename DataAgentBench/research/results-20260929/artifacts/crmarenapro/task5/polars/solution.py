import json
from datetime import date
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
PRODUCT = '01tWt000006hV8LIAU'
TODAY = date(2023, 1, 16)

def clean_id(name):
    return pl.col(name).str.strip_chars().str.strip_prefix('#')

items = (
    pl.scan_parquet(DATA / 'products_orders/OrderItem.parquet')
    .select(clean_id('Id').alias('orderitemid__c'), clean_id('Product2Id'))
    .filter(pl.col('Product2Id') == PRODUCT)
    .select('orderitemid__c')
)
cases = (
    pl.scan_parquet(DATA / 'support/Case.parquet')
    .select(clean_id('id'), clean_id('orderitemid__c'), clean_id('issueid__c'),
            pl.col('createddate').str.slice(0, 10).str.to_date().alias('created_day'))
)
# Rolling five calendar months through the supplied current date.
counts = (
    cases.join(items, on='orderitemid__c', how='semi')
    .filter(pl.col('created_day').is_between(pl.lit(TODAY).dt.offset_by('-5mo'), pl.lit(TODAY)))
    .filter(pl.col('issueid__c').is_not_null() & (pl.col('issueid__c') != ''))
    .group_by('issueid__c').len(name='reports')
    .sort(['reports', 'issueid__c'], descending=[True, False])
    .collect()
)
assert counts.height, 'No qualifying cases'
assert counts.height == 1 or counts['reports'][0] > counts['reports'][1], 'Tied most frequent issues'
counts.write_csv(OUT / 'issue_counts.csv')
answer = counts['issueid__c'][0]
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(counts)
print(json.dumps({'answer': answer}))
