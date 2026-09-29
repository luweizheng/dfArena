import json
from pathlib import Path
import ibis

@ibis.udf.scalar.builtin
def try_strptime(value: str, format: str) -> ibis.expr.datatypes.timestamp:
    ...


def main():
    con = ibis.duckdb.connect()
    reviews = con.read_parquet('/workspace/data/review/review.parquet')
    businesses = con.read_parquet('/workspace/data/business/business_description.parquet')
    parsed = ibis.coalesce(
        try_strptime(reviews.time, '%Y-%m-%d %H:%M:%S'),
        try_strptime(reviews.time, '%B %d, %Y at %I:%M %p'),
        try_strptime(reviews.time, '%d %b %Y, %H:%M'),
    )
    dated = reviews.mutate(review_time=parsed)
    invalid = dated.filter(dated.review_time.isnull()).count().execute()
    assert invalid == 0, f'{invalid} unparsed timestamps'
    eligible = dated.filter((dated.review_time.year() == 2019) & (dated.rating >= 4.5))
    counts = eligible.group_by('gmap_id').aggregate(high_rating_reviews=eligible.count())
    names = businesses.select('gmap_id', 'name').distinct()
    assert names.count().execute() == names.gmap_id.nunique().execute()
    ranked = counts.join(names, 'gmap_id').select(
        counts.gmap_id, names.name, counts.high_rating_reviews
    ).order_by(ibis.desc('high_rating_reviews'), 'name', 'gmap_id')
    rows = ranked.limit(3).to_pyarrow().to_pylist()
    assert len(rows) == 3
    answer = '; '.join(f"{row['name']}: {row['high_rating_reviews']} high-rating reviews" for row in rows) + '.'
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(answer)

if __name__ == '__main__':
    main()
