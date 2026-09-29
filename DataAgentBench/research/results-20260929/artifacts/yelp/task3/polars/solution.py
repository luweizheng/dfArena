import ast
import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def offers_parking(raw):
    if raw is None:
        return False
    attrs = json.loads(raw)
    bike = attrs.get('BikeParking') == 'True'
    parking_text = attrs.get('BusinessParking')
    # Parse the Python-literal dictionary safely, without executing code.
    parking = ast.literal_eval(parking_text) if parking_text else None
    business = isinstance(parking, dict) and any(v is True for v in parking.values())
    return bike or business

reviews = pl.scan_parquet(DATA / 'user/review.parquet')
year = pl.col('date').str.extract(r'\b((?:19|20)\d{2})\b', 1)
# Dates have mixed textual formats, but all contain an explicit four-digit year.
assert reviews.select(year.is_null().sum()).collect().item() == 0
reviewed = (
    reviews.filter(year == '2018')
    .select(pl.col('business_ref').str.replace(r'^businessref_', 'businessid_').alias('business_id'))
    .unique()
)
businesses = pl.scan_parquet(DATA / 'businessinfo/business.parquet')
qualifying = (
    businesses.join(reviewed, on='business_id', how='semi')
    .filter(pl.col('attributes').map_elements(offers_parking, return_dtype=pl.Boolean))
    .select('business_id').unique().collect()
)
count = qualifying.height
qualifying.write_csv(OUT / 'qualifying_businesses.csv')
answer = {'answer': f'{count} businesses.'}
(OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
print(json.dumps(answer))
