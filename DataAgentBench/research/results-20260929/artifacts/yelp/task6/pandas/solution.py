import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
reviews = pd.read_parquet(DATA / 'user/review.parquet', columns=['business_ref', 'rating', 'date'])
businesses = pd.read_parquet(DATA / 'businessinfo/business.parquet', columns=['business_id', 'name', 'description'])
# Source dates use several text formats. Fail on any unparseable date.
dates = pd.to_datetime(reviews['date'], format='mixed', errors='raise')
period = reviews.loc[(dates >= pd.Timestamp('2016-01-01')) & (dates < pd.Timestamp('2016-07-01'))]
stats = period.groupby('business_ref')['rating'].agg(average='mean', reviews='size')
eligible = stats.loc[stats['reviews'] >= 5].copy()
assert not eligible.empty
eligible['business_id'] = eligible.index.str.replace(r'^businessref_', 'businessid_', regex=True)
winners = eligible.loc[eligible['average'].eq(eligible['average'].max())].merge(businesses, on='business_id', validate='one_to_one')
assert not winners.empty

def categories(description):
    # Extract the category list from the natural-language business description.
    match = re.search(r'menu featuring (.*?)(?:, perfect for|\.$)', description)
    if not match:
        raise ValueError('Unrecognized category description: ' + description)
    return match.group(1).strip().rstrip('.')

answers = []
for row in winners.itertuples(index=False):
    answers.append(f'{row.name} — categories: {categories(row.description)}; average rating {row.average:g}/5 from {row.reviews} reviews (January 1–June 30, 2016).')
answer = {'answer': ' '.join(answers)}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))
