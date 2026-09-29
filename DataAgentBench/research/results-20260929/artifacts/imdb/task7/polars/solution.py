from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def scan(group, table):
    return pl.scan_parquet(DATA / group / f'{table}.parquet')

def numeric(column):
    return pl.col(column).str.replace_all(r'[^0-9]', '').cast(pl.Int64)

keywords = scan('movies', 'keyword').filter(
    pl.col('keyword') == 'character-name-in-title'
).select(numeric('id').alias('keyword_id'))
keyword_movies = scan('movies', 'movie_keyword').select(
    pl.col('movie_id').cast(pl.Int64), numeric('keyword_id')
).join(keywords, on='keyword_id', how='semi').select('movie_id').unique()
us_companies = scan('movies', 'company_name').filter(
    pl.col('country_code') == '[us]'
).select(numeric('id').alias('company_id'))
us_movies = scan('movies', 'movie_companies').select(
    pl.col('movie_id').cast(pl.Int64), pl.col('company_id').cast(pl.Int64)
).join(us_companies, on='company_id', how='semi').select('movie_id').unique()
# All title types and all cast/crew roles qualify; company role is unrestricted.
titles = scan('movies', 'title').select(
    numeric('id').alias('movie_id'), 'title'
).join(keyword_movies, on='movie_id', how='semi').join(us_movies, on='movie_id', how='semi')
credits = scan('people', 'cast_info').select(
    numeric('person_id'), pl.col('movie_id').cast(pl.Int64)
).join(titles, on='movie_id', how='inner')
aliases = scan('people', 'aka_name').select('person_id', pl.col('name').alias('pseudonym'))
qualified = credits.join(aliases, on='person_id', how='inner')
# Independent minima over the same qualifying relation, not a paired first row.
result = qualified.select(pl.col('pseudonym').min(), pl.col('title').min()).collect(engine='streaming').row(0, named=True)
answer = f"Pseudonym: {result['pseudonym']}; title: {result['title']}."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(json.dumps({'answer': answer}, ensure_ascii=False))

if __name__ == '__main__':
    pass
