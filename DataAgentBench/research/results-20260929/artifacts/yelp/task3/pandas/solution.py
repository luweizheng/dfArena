import ast
import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def offers_parking(cell):
    attrs = json.loads(cell) if pd.notna(cell) else {}
    bike = attrs.get('BikeParking') == 'True'
    parking_text = attrs.get('BusinessParking')
    # Parse literal data safely; never execute attribute strings.
    parking = ast.literal_eval(parking_text) if parking_text else None
    business = parking is True or (
        isinstance(parking, dict) and any(v is True for v in parking.values())
    )
    return bike or business

def main():
    businesses = pd.read_parquet(DATA / 'businessinfo/business.parquet',
                                 columns=['business_id', 'attributes'])
    reviews = pd.read_parquet(DATA / 'user/review.parquet',
                              columns=['business_ref', 'date'])
    dates = pd.to_datetime(reviews['date'], format='mixed', errors='raise')
    reviewed = reviews.loc[(dates >= '2018-01-01') & (dates < '2019-01-01'),
                           'business_ref'].str.replace(r'^businessref_', 'businessid_', regex=True)
    eligible = businesses['attributes'].map(offers_parking)
    count = businesses.loc[eligible & businesses['business_id'].isin(reviewed),
                           'business_id'].nunique()
    answer = {'answer': f'{count} businesses.'}
    (OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(answer))

if __name__ == '__main__':
    main()
