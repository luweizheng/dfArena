import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def categories(description):
    # Category lists occur after one of these prose introductions.
    patterns = [
        r'in the categor(?:y|ies) of ', r'in the fields? of ',
        r'in the realm of ', r'including ', r'services in ',
        r'solutions in ', r'specializes in ', r'destination for ',
        r'anyone seeking ', r'those seeking ', r'ranging from ',
        r'delightful mix of ', r'menu featuring ', r'options for ',
        r'for enjoying delicious ', r'experience encompassing ',
    ]
    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            tail = description[match.end():]
            break
    else:
        raise ValueError(f'Unknown category introduction: {description}')
    # Stop at narrative clauses following the category enumeration.
    tail = re.split(r', (?:making|providing|offering|catering|perfect|ensuring)\b| to (?:meet|keep)\b', tail)[0]
    if tail.startswith('Automotive services') and 'Car Wash' in description:
        # This description expresses two categories in a prose clause.
        tail = 'Automotive, Car Wash, Auto Detailing'
    result = []
    for item in tail.rstrip('.').split(','):
        item = re.sub(r'^(?:and |to |a )+', '', item.strip()).strip("'")
        item = re.sub(r' services$', '', item)
        if item:
            result.append(item)
    return list(dict.fromkeys(result))

users = pd.read_parquet(DATA / 'user/user.parquet', columns=['user_id', 'yelping_since'])
reviews = pd.read_parquet(DATA / 'user/review.parquet', columns=['user_id', 'business_ref', 'date'])
businesses = pd.read_parquet(DATA / 'businessinfo/business.parquet', columns=['business_id', 'description'])
registered = pd.to_datetime(users['yelping_since'], format='mixed', errors='raise')
review_dates = pd.to_datetime(reviews['date'], format='mixed', errors='raise')
cohort = users.loc[registered.dt.year.eq(2016), 'user_id']
selected = reviews.loc[reviews['user_id'].isin(cohort) & review_dates.ge(pd.Timestamp('2016-01-01'))].copy()
selected['business_id'] = selected['business_ref'].str.replace(r'^businessref_', 'businessid_', regex=True)
joined = selected.merge(businesses, on='business_id', how='left', validate='many_to_one')
assert joined['description'].notna().all()
joined['category'] = joined['description'].map(categories)
joined[['business_id', 'description', 'category']].drop_duplicates('business_id').to_json(OUT / 'category_audit.json', orient='records', indent=2)
counts = (joined.explode('category').groupby('category').size().rename('reviews').reset_index()
          .sort_values(['reviews', 'category'], ascending=[False, True]))
counts.to_csv(OUT / 'category_counts.csv', index=False)
top = counts.head(5)
answer = '; '.join(f'{row.category}: {row.reviews} reviews' for row in top.itertuples()) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(counts.head(15).to_string(index=False))
print(answer)
