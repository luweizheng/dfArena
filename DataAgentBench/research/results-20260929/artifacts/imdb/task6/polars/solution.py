import json
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
def table(group, name):
    return pl.scan_parquet(ROOT / group / f'{name}.parquet')
def numeric(column):
    return pl.col(column).str.extract(r'(\d+)', 1).cast(pl.Int64)
def lookup(group, name, label, value):
    return table(group, name).filter(pl.col(label) == value).select(pl.col('id').cast(pl.String).str.extract(r'(\d+)',1).cast(pl.Int64)).collect().item()

trivia = lookup('movies', 'info_type', 'info', 'trivia')
release = lookup('movies', 'info_type', 'info', 'release dates')
actress = lookup('people', 'role_type', 'role', 'actress')
cast = lookup('movies', 'comp_cast_type', 'kind', 'cast')
verified = lookup('movies', 'comp_cast_type', 'kind', 'complete+verified')

people = (table('people', 'name')
    .filter((pl.col('gender') == 'f') & pl.col('name').str.contains('An', literal=True))
    .select(numeric('id').alias('person_id'), pl.col('name').alias('actress'))
    .join(table('people','aka_name').select('person_id'), on='person_id', how='semi')
    .join(table('people','person_info').filter(pl.col('info_type_id') == trivia).select('person_id'), on='person_id', how='semi'))
keywords = table('movies','keyword').filter(pl.col('keyword') == 'computer-animation').select(numeric('id').alias('keyword_id'))
animated = table('movies','movie_keyword').with_columns(numeric('keyword_id')).join(keywords, on='keyword_id', how='semi').select(pl.col('movie_id').cast(pl.Int64))
companies = table('movies','company_name').filter(pl.col('country_code') == '[us]').select(numeric('id').alias('company_id'))
us_movies = table('movies','movie_companies').with_columns(pl.col('company_id').cast(pl.Int64)).join(companies, on='company_id', how='semi').select(pl.col('movie_id').cast(pl.Int64))
releases = (table('movies','movie_info').with_columns(numeric('info_type_id'))
    .filter((pl.col('info_type_id') == release) & pl.col('info').str.contains(r'^(Japan|USA):.*200[0-9]'))
    .select(pl.col('movie_id').cast(pl.Int64)))
complete = (table('movies','complete_cast').filter((pl.col('subject_id') == cast) & (pl.col('status_id') == verified))
    .select(pl.col('movie_id').cast(pl.Int64)))
movies = table('movies','title').filter(pl.col('production_year').is_between(2000,2010)).select(numeric('id').alias('movie_id'),'title')
for restriction in [animated, us_movies, releases, complete]:
    movies = movies.join(restriction, on='movie_id', how='semi')
voices = ['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)']
credits = (table('people','cast_info').filter((pl.col('role_id') == actress) & pl.col('note').is_in(voices))
    .select(numeric('person_id'), 'movie_id','person_role_id')
    .join(people, on='person_id').join(movies,on='movie_id')
    .join(table('people','char_name').select(pl.col('id').alias('person_role_id'),pl.col('name').alias('character')),on='person_role_id'))
result = credits.select('character','actress','title').collect()
result.write_csv(OUT / 'matching_credits.csv')
minima = result.select(pl.all().min()).row(0, named=True)
answer = f"Character: {minima['character']}; actress: {minima['actress']}; title: {minima['title']}."
(OUT / 'answer.json').write_text(json.dumps({'answer':answer}) + '\n')
print(json.dumps({'matching_rows':result.height, **minima}))
