import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    businesses = con.read_parquet('/workspace/data/business/business_description.parquet')
    reviews = con.read_parquet('/workspace/data/review/review.parquet')
    local = businesses.filter(
        businesses.description.re_search(r'(?i)\bLos Angeles,\s*(CA\b|California\b)')
    ).select('gmap_id', 'name').distinct()
    averages = reviews.group_by('gmap_id').aggregate(average_rating=reviews.rating.mean())
    ranked = (local.join(averages, 'gmap_id')
              .select(local.name, local.gmap_id, averages.average_rating)
              .filter(averages.average_rating.notnull())
              .order_by(ibis.desc('average_rating'), ibis.asc('name'), ibis.asc('gmap_id'))
              .limit(5))
    rows = ranked.to_pyarrow().to_pylist()
    answer = '; '.join(
        f"{i}. {row['name']} — {row['average_rating']:.2f}/5"
        for i, row in enumerate(rows, 1)
    )
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(answer)


if __name__ == '__main__':
    main()
