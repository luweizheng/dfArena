from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
def scan(group, table):
    return pl.scan_parquet(DATA / group / f'{table}.parquet')
def numeric(column):
    return pl.col(column).str.extract(r'(\d+)', 1).cast(pl.Int64)

# Normalize encoded text identifiers before joining to numeric foreign keys.
actresses = (scan('people', 'name').filter(pl.col('gender') == 'f')
    .select(numeric('id').alias('person_id'), pl.col('name').alias('actress'))
    .join(scan('people', 'aka_name').select('person_id'), on='person_id', how='semi'))
roles = (scan('people', 'role_type').filter(pl.col('role') == 'actress')
    .select(numeric('id').alias('role_id')))
characters = scan('people', 'char_name').select(pl.col('id').alias('person_role_id'))
voice_notes = ['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)']
credits = (scan('people', 'cast_info').filter(pl.col('note').is_in(voice_notes))
    .select(numeric('person_id').alias('person_id'), 'movie_id', 'person_role_id', 'role_id')
    .join(roles, on='role_id', how='semi')
    .join(characters, on='person_role_id', how='semi')
    .join(actresses, on='person_id'))
us_companies = (scan('movies', 'company_name').filter(pl.col('country_code') == '[us]')
    .select(numeric('id').alias('company_id')))
us_titles = (scan('movies', 'movie_companies').select(pl.col('company_id').cast(pl.Int64), pl.col('movie_id').cast(pl.Int64))
    .join(us_companies, on='company_id', how='semi').select('movie_id'))
release_types = (scan('movies', 'info_type').filter(pl.col('info') == 'release dates')
    .select(numeric('id').alias('info_type_id')))
released_titles = (scan('movies', 'movie_info')
    .select(pl.col('movie_id').cast(pl.Int64), numeric('info_type_id').alias('info_type_id'))
    .join(release_types, on='info_type_id', how='semi').select('movie_id'))
titles = (scan('movies', 'title').filter(pl.col('production_year') > 2000)
    .select(numeric('id').alias('movie_id'), 'title')
    .join(us_titles, on='movie_id', how='semi')
    .join(released_titles, on='movie_id', how='semi'))
qualified = credits.join(titles, on='movie_id').select('actress', 'title').collect(engine='streaming')
# The two alphabetical minima are computed independently over qualifying rows.
result = qualified.select(pl.col('actress').min(), pl.col('title').min()).row(0, named=True)
assert qualified.height and all(result.values())
answer = f"Actress: {result['actress']}; title: {result['title']}."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(json.dumps({'qualifying_credits': qualified.height, **result}, ensure_ascii=False))

if __name__ == '__main__':
    pass
