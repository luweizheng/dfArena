import json
import re
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
business = con.read_parquet(str(ROOT / 'businessinfo/business.parquet'))
users = con.read_parquet(str(ROOT / 'user/user.parquet'))
reviews = con.read_parquet(str(ROOT / 'user/review.parquet'))

@ibis.udf.scalar.python
def categories(description: str) -> list[str]:
    # Category names are embedded in prose after the business introduction.
    body = re.split(r'\b(?:offers|specializes|provides|showcasing)\b', description, maxsplit=1)[-1]
    word = r"[A-Z][A-Za-z'/-]*(?:\s+\((?:New|Traditional)\))?"
    pattern = word + r'(?:\s+(?:&\s+)?' + word + r')*'
    found = re.findall(pattern, body)
    # A few descriptions render category names in lowercase prose.
    for phrase in re.findall(r'\b(?:nightlife|bars|restaurants|sports bars)\b', body):
        found.append(phrase.title())
    # This single category contains commas internally.
    if 'Books, Mags, Music & Video' in body:
        found = [x for x in found if x not in ('Books', 'Mags', 'Music & Video')]
        found.append('Books, Mags, Music & Video')
    return sorted(set(found))

# Each available date format contains a four-digit year. Year extraction is
# sufficient for both whole-calendar-year registration and the inclusive cutoff.
def year(column):
    return column.re_extract(r'\b((?:19|20)\d{2})\b', 1).cast('int32')

cohort = users.filter(year(users.yelping_since) == 2016).select('user_id').distinct()
qualifying = reviews.filter(year(reviews.date) >= 2016).semi_join(cohort, 'user_id')
counts = qualifying.group_by('business_ref').aggregate(review_total=ibis._.count())
category_rows = business.select(
    business_ref=business.business_id.re_replace(r'^businessid_', 'businessref_'),
    category=categories(business.description).unnest(),
).distinct()
joined = counts.join(category_rows, 'business_ref')
ranked = joined.group_by('category').aggregate(total_reviews=joined.review_total.sum()).order_by(ibis.desc('total_reviews'), 'category')
result = ranked.limit(5).to_pyarrow().to_pylist()
# Save the parsed dimension and full ranking to make the extraction auditable.
(OUT / 'category_audit.json').write_text(json.dumps(category_rows.order_by('business_ref', 'category').to_pyarrow().to_pylist(), indent=2))
(OUT / 'ranking.json').write_text(json.dumps(ranked.to_pyarrow().to_pylist(), indent=2))
answer = '; '.join(f"{row['category']}: {row['total_reviews']} reviews" for row in result) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(answer)
