import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
business = pd.read_parquet(DATA / 'businessinfo/business.parquet')
attrs = business['attributes'].map(lambda x: json.loads(x) if pd.notna(x) else {})
eligible = business.loc[attrs.map(lambda x: x.get('BusinessAcceptsCreditCards') == 'True')].copy()
# Category names appear as capitalized phrases in the descriptive prose.
# Remove the location prefix before extracting the category vocabulary.
bodies = business['description'].str.replace(r'^.*?, this ', '', regex=True)
word = r"[A-Z][A-Za-z'/-]*(?:\s*\([A-Za-z]+\))?"
phrase = rf'{word}(?:(?:\s+&\s+|\s+){word})*'
vocabulary = sorted({m.group(0) for body in bodies.dropna() for m in re.finditer(phrase, body)})
# Match vocabulary case-insensitively to include categories rendered in lowercase.
# Keep category boundaries so Bars does not also count Wine Bars or Sports Bars.
rows = []
for idx, row in eligible.iterrows():
    body = bodies.loc[idx]
    matches = []
    for category in vocabulary:
        for match in re.finditer(r'(?<![\w])' + re.escape(category) + r'(?![\w])', body, re.I):
            matches.append((match.start(), match.end(), category))
    categories = {c for s, e, c in matches if not any(s2 <= s and e2 >= e and (s2 < s or e2 > e) for s2, e2, _ in matches)}
    rows.extend((row['business_id'], c) for c in categories)
category_business = pd.DataFrame(rows, columns=['business_id', 'category']).drop_duplicates()
counts = category_business.groupby('category')['business_id'].nunique().sort_values(ascending=False)
winners = counts[counts == counts.max()]
reviews = pd.read_parquet(DATA / 'user/review.parquet', columns=['business_ref', 'rating'])
results = []
for category, count in winners.items():
    ids = category_business.loc[category_business.category.eq(category), 'business_id'].str.replace('businessid_', 'businessref_', n=1, regex=False)
    ratings = reviews.loc[reviews.business_ref.isin(ids), 'rating']
    results.append(f'{category} has the most businesses accepting credit cards ({count}), with an average rating of {ratings.mean():.2f}/5.')
    print(category, int(count), len(ratings), ratings.mean())
counts.to_csv(OUT / 'category_counts.csv')
(OUT / 'answer.json').write_text(json.dumps({'answer': ' '.join(results)}) + '\n')
print(counts.head(10).to_string())
