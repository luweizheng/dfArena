import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def scan(group, table):
    return pl.scan_parquet(DATA / group / f'{table}.parquet')

def numeric(column):
    return pl.col(column).str.extract(r'([0-9]+)', 1).cast(pl.Int64)

def main():
    keywords = scan('movies', 'keyword').filter(
        pl.col('keyword') == 'character-name-in-title'
    ).select(numeric('id').alias('keyword_id'))
    tagged = scan('movies', 'movie_keyword').select(
        pl.col('movie_id').cast(pl.Int64), numeric('keyword_id')
    ).join(keywords, on='keyword_id', how='semi').select('movie_id')
    companies = scan('movies', 'movie_companies').select(
        pl.col('movie_id').cast(pl.Int64)
    )
    titles = scan('movies', 'title').select(numeric('id').alias('movie_id'))
    eligible = tagged.join(companies, on='movie_id', how='semi').join(
        titles, on='movie_id', how='semi'
    ).unique()
    names = scan('people', 'name').filter(pl.col('name').str.starts_with('Z')).select(
        numeric('id').alias('person_id'), 'name'
    )
    credits = scan('people', 'cast_info').select(
        numeric('person_id'), pl.col('movie_id').cast(pl.Int64)
    ).join(eligible, on='movie_id', how='semi')
    result = names.join(credits, on='person_id', how='semi').select('name').unique().sort('name').collect(engine='streaming')
    if result.is_empty():
        raise ValueError('No qualifying names')
    answer = result.item(0, 'name')
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(result.head(10))
    print(json.dumps({'answer': answer}, ensure_ascii=False))

if __name__ == '__main__':
    main()
