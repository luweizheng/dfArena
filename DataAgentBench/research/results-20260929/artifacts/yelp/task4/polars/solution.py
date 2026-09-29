import json
import re
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')

# Categories appear as capitalized names in the descriptive prose. Remove
# the location first so city/street names cannot be counted as categories.
word = r"[A-Z][A-Za-z'-]*(?:/[A-Za-z]+)*"
category_pattern = re.compile(
    rf"\b{word}(?:(?:\s+|\s*&\s*){word}|\s+\([A-Za-z]+\))*"
)
def categories(description):
    if not description:
        return []
    body = re.split(r'\b(?:offers|specializes in|provides|showcasing)\b', description, maxsplit=1)[-1]
    names = category_pattern.findall(body)
    # This description renders some of its category list in lower case.
    lower_list = re.search(r'perfect for (nightlife, bars, restaurants, and sports bars)', body)
    if lower_list:
        names.extend(x.strip().removeprefix('and ').title() for x in lower_list.group(1).split(','))
    # A category containing commas must remain one category.
    if 'Books, Mags, Music & Video' in body:
        names = [x for x in names if x not in {'Books', 'Mags', 'Music & Video'}]
        names.append('Books, Mags, Music & Video')
    return sorted(set(names))

businesses = pl.read_parquet(ROOT / 'businessinfo/business.parquet')
eligible = businesses.filter(
    pl.col('attributes').map_elements(
        lambda value: json.loads(value).get('BusinessAcceptsCreditCards') == 'True',
        return_dtype=pl.Boolean,
    ).fill_null(False)
).with_columns(
    pl.col('description').map_elements(categories, return_dtype=pl.List(pl.String)).alias('category'),
    pl.col('business_id').str.replace(r'^businessid_', 'businessref_').alias('business_ref'),
)
memberships = eligible.select('business_id', 'business_ref', 'category').explode('category').drop_nulls('category').unique()
counts = memberships.group_by('category').agg(pl.col('business_id').n_unique().alias('business_count')).sort(['business_count', 'category'], descending=[True, False])
winners = counts.filter(pl.col('business_count') == counts['business_count'].max())
reviews = pl.scan_parquet(ROOT / 'user/review.parquet').select('business_ref', 'rating')
results = []
for row in winners.iter_rows(named=True):
    refs = memberships.filter(pl.col('category') == row['category']).select('business_ref').unique()
    stats = reviews.join(refs.lazy(), on='business_ref', how='semi').select(pl.col('rating').mean().alias('average_rating'), pl.len().alias('review_count')).collect().row(0, named=True)
    results.append({**row, **stats})
counts.write_csv(OUT / 'category_counts.csv')
(OUT / 'calculation.json').write_text(json.dumps(results, indent=2))
answer = '; '.join(f"{r['category']} ({r['business_count']} businesses accepting credit cards), with an average rating of {r['average_rating']:.2f}/5" for r in results) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(counts.head(10))
print(json.dumps(results, indent=2))
print(answer)
