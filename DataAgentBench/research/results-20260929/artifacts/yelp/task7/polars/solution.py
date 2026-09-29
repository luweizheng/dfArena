import json
import re
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')

# Category lists are embedded in prose. Extract the list after its introductory
# phrase and remove narrative suffixes, preserving category punctuation.
def categories(description):
    markers = [
        r'including ', r'in the categories of ', r'in the category of ',
        r'in the fields of ', r'in the field of ', r'in the realm of ',
        r'range of services in ', r'variety of services in ',
        r'range of solutions in ', r'destination for ', r'anyone seeking ',
        r'options ranging from ', r'specializes in ', r'delightful mix of ',
        r'menu featuring ', r'options for ', r'for enjoying delicious ',
        r'for those seeking ', r'experience encompassing ',
    ]
    # Earliest matching introduction handles overlapping generic phrases.
    matches = [m for pat in markers if (m := re.search(pat, description))]
    if not matches:
        raise ValueError(f'Unrecognized description: {description}')
    match = min(matches, key=lambda m: m.start())
    listing = description[match.end():].strip().strip("'.")
    listing = listing.replace(', offering a comprehensive ', ', ').replace(' and professional ', ', ')
    listing = re.sub(r' to keep.*', '', listing)
    listing = re.split(r', (?:making|providing|offering|catering|perfect|ensuring)\b| to meet\b', listing)[0]
    # One description expresses its categories in a sentence instead of a list.
    listing = re.sub(r' services\b', '', listing)
    listing = listing.replace(' and a Wine Tasting Room', ' Wine Tasting Room')
    listing = listing.replace('a Wine Tasting Room', 'Wine Tasting Room')
    if 'offering a comprehensive' in listing:
        listing = re.sub(r', offering a comprehensive ', ', ', listing)
        listing = re.sub(r' and professional ', ', ', listing)
        listing = re.sub(r' to keep.*', '', listing)
    result = []
    for part in listing.split(','):
        part = re.sub(r'^(?:and |to )', '', part.strip()).strip("'. ")
        if part and part not in result:
            result.append(part)
    return result

def parse_date(column):
    return pl.coalesce([pl.col(column).str.strptime(pl.Datetime, fmt, strict=False) for fmt in ['%d %b %Y, %H:%M', '%B %d, %Y at %I:%M %p', '%Y-%m-%d %H:%M:%S']])

for table, column in [('user', 'yelping_since'), ('review', 'date')]:
    dates = pl.read_parquet(ROOT / f'user/{table}.parquet', columns=[column])
    assert dates.select(parse_date(column).is_null().sum()).item() == 0

users = pl.scan_parquet(ROOT / 'user/user.parquet').with_columns(
    parse_date('yelping_since').alias('registered')
).filter(pl.col('registered').dt.year() == 2016).select('user_id')
reviews = pl.scan_parquet(ROOT / 'user/review.parquet').with_columns(
    parse_date('date').alias('review_date')
).filter(pl.col('review_date') >= pl.datetime(2016, 1, 1)).join(users, on='user_id', how='semi')
counts = reviews.group_by('business_ref').agg(pl.len().alias('reviews'))
businesses = pl.scan_parquet(ROOT / 'businessinfo/business.parquet').with_columns(
    pl.col('business_id').str.replace(r'^businessid_', 'businessref_').alias('business_ref')
).join(counts, on='business_ref', how='inner').select('business_ref', 'description', 'reviews').collect()
assert businesses['business_ref'].n_unique() == businesses.height
categorized = businesses.with_columns(
    pl.col('description').map_elements(categories, return_dtype=pl.List(pl.String)).alias('category')
)
categorized.write_json(OUT / 'category_audit.json')
ranking = categorized.explode('category').group_by('category').agg(
    pl.col('reviews').sum()
).sort(['reviews', 'category'], descending=[True, False])
ranking.write_csv(OUT / 'category_counts.csv')
top = ranking.head(5)
answer = '; '.join(f'{r["category"]}: {r["reviews"]} reviews' for r in top.to_dicts()) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(ranking.head(15))
print(answer)
