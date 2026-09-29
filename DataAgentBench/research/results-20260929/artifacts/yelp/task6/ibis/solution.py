import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
business = con.read_parquet('/workspace/data/businessinfo/business.parquet')
review = con.read_parquet('/workspace/data/user/review.parquet')
parsed_date = ibis.cases(
    (review.date.contains(' at '), review.date.as_timestamp('%B %d, %Y at %I:%M %p')),
    (review.date.re_search(r'^\d{2} [A-Za-z]{3} '), review.date.as_timestamp('%d %b %Y, %H:%M')),
    else_=review.date.as_timestamp('%Y-%m-%d %H:%M:%S'),
)
reviews = review.mutate(review_date=parsed_date)
period = reviews.filter(
    reviews.review_date >= ibis.timestamp('2016-01-01'),
    reviews.review_date < ibis.timestamp('2016-07-01'),
)
ratings = period.group_by('business_ref').aggregate(
    average_rating=period.rating.mean(), period_review_count=period.count()
)
qualified = ratings.filter(ratings.period_review_count >= 5)
businesses = business.mutate(business_ref=business.business_id.replace('businessid_', 'businessref_'))
ranked = qualified.join(businesses, 'business_ref').select(
    'business_id', 'name', 'description', 'average_rating', 'period_review_count'
).order_by(ibis.desc('average_rating'), 'business_id')
rows = ranked.to_pyarrow().to_pylist()
assert rows, 'No eligible businesses'
(OUT / 'ranked_results.json').write_text(json.dumps(rows, indent=2))
print(json.dumps(rows, indent=2))

# Extract the category list from the winning business's description.
import re
winners = [row for row in rows if row['average_rating'] == rows[0]['average_rating']]
answers = []
for row in winners:
    match = re.search(
        r'(?:featuring |services in |services, including |services including )(.+?)(?:, perfect for\b| to meet\b|\.$)',
        row['description'],
    )
    assert match, 'Category wording requires inspection'
    categories = match.group(1).strip()
    answers.append(
        f"{row['name']} — categories: {categories}; average rating "
        f"{row['average_rating']:g}/5 from {row['period_review_count']} reviews "
        "during January 1–June 30, 2016."
    )
(OUT / 'answer.json').write_text(json.dumps({'answer': ' '.join(answers)}, ensure_ascii=False) + '\n')
