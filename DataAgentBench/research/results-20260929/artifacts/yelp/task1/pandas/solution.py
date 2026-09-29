import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
business = pd.read_parquet(DATA / 'businessinfo/business.parquet', columns=['business_id', 'description'])
review = pd.read_parquet(DATA / 'user/review.parquet', columns=['business_ref', 'rating'])
located = business['description'].str.contains(r'\bin Indianapolis,\s*(?:IN|Indiana)\b', case=False, na=False, regex=True)
references = business.loc[located, 'business_id'].str.replace(r'^businessid_', 'businessref_', regex=True)
ratings = review.loc[review['business_ref'].isin(references), 'rating']
assert len(ratings) > 0, 'No matching reviews'
average = ratings.mean()
answer = {'answer': f'The average rating of businesses in Indianapolis, Indiana is {average:.4f} out of 5.'}
(OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
print(json.dumps({'businesses': int(located.sum()), 'reviews': len(ratings), 'rating_sum': int(ratings.sum()), 'average_rating': float(average)}))
print(json.dumps(answer))
