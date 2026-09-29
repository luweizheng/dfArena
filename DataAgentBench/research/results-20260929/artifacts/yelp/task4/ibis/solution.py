import json
import re
from pathlib import Path
import ibis

OUT = Path('/workspace/work')

@ibis.udf.scalar.python
def categories(description: str) -> list[str]:
    if description is None:
        return []
    # Categories are title-cased lists embedded after the location sentence prefix.
    body = re.split(r', [A-Z]{2}, ', description, maxsplit=1)[-1]
    # One description renders its category list in lowercase prose.
    body = re.sub(r'\b(nightlife|bars|restaurants|sports bars)\b',
                  lambda m: m.group(0).title(), body)
    pattern = r"\b[A-Z][A-Za-z'/-]*(?: (?:& )?(?:[A-Z][A-Za-z'/-]*|\([A-Z][a-z]+\)))*"
    found = re.findall(pattern, body)
    # This Yelp category itself contains commas.
    if 'Books, Mags, Music & Video' in body:
        found = [x for x in found if x not in ('Books', 'Mags', 'Music & Video')]
        found.append('Books, Mags, Music & Video')
    return sorted(set(found))

con = ibis.duckdb.connect()
business = con.read_parquet('/workspace/data/businessinfo/business.parquet')
reviews = con.read_parquet('/workspace/data/user/review.parquet')
accepting = business.filter(
    business.attributes.cast('json')['BusinessAcceptsCreditCards'].str == 'True'
)
expanded = accepting.select(
    'business_id',
    category=categories(accepting.description).unnest(),
).distinct()
counts = expanded.group_by('category').aggregate(business_count=expanded.business_id.nunique())
leaders = counts.filter(counts.business_count == counts.business_count.max())
selected = expanded.join(leaders, 'category').select(
    expanded.category,
    leaders.business_count,
    business_ref=expanded.business_id.replace('businessid_', 'businessref_'),
)
selected = selected.view()
matched = selected.join(reviews, 'business_ref')
result = matched.group_by('category', 'business_count').aggregate(
    average_rating=matched.rating.mean(), review_count=matched.count()
).order_by('category')
rows = result.to_pyarrow().to_pylist()
assert rows, 'No matching reviews'
(OUT / 'category_counts.json').write_text(json.dumps(
    counts.order_by(ibis.desc('business_count'), 'category').to_pyarrow().to_pylist(), indent=2))
(OUT / 'result_details.json').write_text(json.dumps(rows, indent=2))
answer = '; '.join(
    f"{r['category']} ({r['business_count']} businesses accepting credit cards), "
    f"with an average rating of {r['average_rating']:.2f} out of 5."
    for r in rows
)
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(answer)
