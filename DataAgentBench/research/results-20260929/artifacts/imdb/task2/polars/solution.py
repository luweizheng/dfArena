import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def scan(group, table):
    return pl.scan_parquet(DATA / group / f'{table}.parquet')

def numeric_id(column):
    return pl.col(column).str.replace_all(r'[^0-9]', '').cast(pl.Int64)

roles = scan('people', 'role_type').filter(pl.col('role') == 'writer').select(numeric_id('id').alias('role_id'))
companies = scan('movies', 'company_name').filter(pl.col('country_code') == '[us]').select(numeric_id('id').alias('company_id'))
us_movies = scan('movies', 'movie_companies').select(pl.col('movie_id').cast(pl.Int64), pl.col('company_id').cast(pl.Int64)).join(companies, on='company_id', how='semi').select('movie_id').unique()
people = scan('people', 'name').select(numeric_id('id').alias('person_id'))
pseudonyms = scan('people', 'aka_name').select('person_id', pl.col('name').alias('pseudonym')).join(people, on='person_id', how='semi')
credits = scan('people', 'cast_info').select(numeric_id('person_id').alias('person_id'), 'movie_id', 'role_id').join(roles, on='role_id', how='semi').join(us_movies, on='movie_id', how='semi')
titles = scan('movies', 'title').select(numeric_id('id').alias('movie_id'), 'title')
qualifying = credits.join(pseudonyms, on='person_id').join(titles, on='movie_id')
# Independent lexical minima over all qualifying pseudonym/title associations.
result = qualifying.select(pl.col('pseudonym').min(), pl.col('title').min(), pl.len().alias('qualifying_rows')).collect(engine='streaming').row(0, named=True)
assert result['qualifying_rows'] > 0
answer = {'answer': f"Pseudonym: {result['pseudonym']}; title: {result['title']}."}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(result, ensure_ascii=False))
print(json.dumps(answer, ensure_ascii=False))

if __name__ == '__main__':
    pass
