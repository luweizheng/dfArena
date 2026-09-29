import json
from datetime import datetime
from pathlib import Path
import ibis

@ibis.udf.scalar.builtin
def try_strptime(value: str, format: str) -> datetime:
    ...


def main():
    con = ibis.duckdb.connect()
    businesses = con.read_parquet('/workspace/data/businessinfo/business.parquet')
    reviews = con.read_parquet('/workspace/data/user/review.parquet')

    parsed = ibis.coalesce(
        try_strptime(reviews.date, '%Y-%m-%d %H:%M:%S'),
        try_strptime(reviews.date, '%B %d, %Y at %I:%M %p'),
        try_strptime(reviews.date, '%d %b %Y, %H:%M'),
    )
    dated = reviews.mutate(review_date=parsed)
    assert dated.filter(dated.review_date.isnull()).count().execute() == 0, 'Unparsed review dates'
    reviewed = dated.filter(dated.review_date.year() == 2018).select(
        business_id=dated.business_ref.re_replace('^businessref_', 'businessid_')
    ).distinct()

    # JSON extraction decodes the preserved outer dictionary. The parking value
    # is a string listing options; match a True option without evaluating code.
    attrs = businesses.attributes.cast('json')
    parking = attrs['BusinessParking'].str
    bike = attrs['BikeParking'].str
    offered = (
        parking.re_search(r':\s*True\s*[,}]').fill_null(False)
        | (bike == 'True').fill_null(False)
    )
    eligible = businesses.filter(offered).select('business_id').distinct()
    count = int(eligible.semi_join(reviewed, 'business_id').count().execute())
    answer = {'answer': f'{count} businesses.'}
    Path('/workspace/work/answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(answer))

if __name__ == '__main__':
    main()
