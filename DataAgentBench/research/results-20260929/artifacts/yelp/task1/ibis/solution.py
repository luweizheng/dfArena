import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    business = con.read_parquet('/workspace/data/businessinfo/business.parquet')
    review = con.read_parquet('/workspace/data/user/review.parquet')
    # Location is embedded in prose; match the city and state together.
    local = business.filter(
        business.description.re_search(r'(?i)\bin Indianapolis,\s*(?:IN|Indiana)\b')
    ).select(business_ref=business.business_id.replace('businessid_', 'businessref_'))
    # A semi join preserves each matching review exactly once.
    reviews = review.semi_join(local, 'business_ref')
    result = reviews.aggregate(average_rating=reviews.rating.mean(), review_count=reviews.count()).to_pyarrow().to_pylist()[0]
    if result['average_rating'] is None:
        raise ValueError('No matching ratings')
    answer = {'answer': f"The average rating is {result['average_rating']:.4f} out of 5."}
    Path('/workspace/work/answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(result))
    print(json.dumps(answer))


if __name__ == '__main__':
    main()
