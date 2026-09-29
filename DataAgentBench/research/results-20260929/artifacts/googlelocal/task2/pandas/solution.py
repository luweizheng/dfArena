import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
businesses = pd.read_parquet(DATA / 'business/business_description.parquet')
reviews = pd.read_parquet(DATA / 'review/review.parquet')

# Descriptions paraphrase massage services as bodywork, soothing treatments,
# body treatments, or rejuvenating treatments and holistic wellness services.
pattern = r'massage|bodywork|soothing treatments|body treatments|holistic wellness'
is_massage = businesses['description'].str.contains(pattern, case=False, na=False)
selected = businesses.loc[is_massage, ['gmap_id', 'name']].drop_duplicates()
averages = reviews.groupby('gmap_id', as_index=False)['rating'].mean()
result = selected.merge(averages, on='gmap_id', how='inner')
result = result.loc[result['rating'].ge(4.0)].sort_values('name')
result.to_csv(OUT / 'qualifying_businesses.csv', index=False)
answer = '; '.join(f"{row.name.strip()}: {row.rating:.2f}" for row in result.itertuples(index=False))
answer += ' (average ratings out of 5, rounded to two decimal places).'
with (OUT / 'answer.json').open('w') as f:
    json.dump({'answer': answer}, f, ensure_ascii=False)
print(json.dumps({'answer': answer}, ensure_ascii=False))
