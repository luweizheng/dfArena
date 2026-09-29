import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    businesses = con.read_parquet('/workspace/data/business/business_description.parquet')
    reviews = con.read_parquet('/workspace/data/review/review.parquet')
    # Descriptions paraphrase massage therapy as bodywork, soothing treatments,
    # or rejuvenating holistic wellness services. Energy healing alone is excluded.
    description = businesses.description.lower().fill_null('')
    massage = businesses.filter(
        description.re_search(
            r'massage|bodywork|soothing body treatments|therapists offer soothing treatments|'
            r'rejuvenating treatments and holistic wellness services'
        )
    ).select('gmap_id', 'name').distinct()
    averages = reviews.group_by('gmap_id').aggregate(average_rating=reviews.rating.mean())
    result = massage.join(averages, 'gmap_id').select(
        massage.name, averages.average_rating
    )
    result = result.filter(result.average_rating >= 4.0).order_by('name')
    rows = result.to_pyarrow().to_pylist()
    def rating_text(value):
        return str(round(value, 2))
    answer = '; '.join(f"{row['name']}: {rating_text(row['average_rating'])}" for row in rows)
    if not rows:
        answer = 'No massage therapy businesses have an average rating of at least 4.0.'
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
