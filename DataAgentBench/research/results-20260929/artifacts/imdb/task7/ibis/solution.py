from pathlib import Path
import json
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
con.raw_sql("SET temp_directory='/workspace/work/duckdb_tmp'")

def table(group, name):
    return con.read_parquet(str(DATA / group / f'{name}.parquet'), table_name=name)

def numeric_id(col):
    return col.re_replace(r'[^0-9]', '').cast('int64')

raw = table('movies', 'title')
titles = raw.select(movie_id=numeric_id(raw.id), title=raw.title)
raw = table('movies', 'keyword')
keywords = raw.filter(raw.keyword == 'character-name-in-title').select(keyword_id=numeric_id(raw.id))
raw = table('movies', 'movie_keyword')
movie_keywords = raw.select('movie_id', keyword_id=numeric_id(raw.keyword_id))
tagged = movie_keywords.semi_join(keywords, 'keyword_id').select('movie_id')
raw = table('movies', 'company_name')
us_companies = raw.filter(raw.country_code == '[us]').select(company_id=numeric_id(raw.id))
companies = table('movies', 'movie_companies')
us_movies = companies.semi_join(us_companies, 'company_id').select('movie_id')
eligible_titles = titles.semi_join(tagged, 'movie_id').semi_join(us_movies, 'movie_id')
raw = table('people', 'cast_info')
credits = raw.select('movie_id', person_id=numeric_id(raw.person_id))
aliases = table('people', 'aka_name').select('person_id', pseudonym='name')
qualified = eligible_titles.inner_join(credits, 'movie_id').inner_join(aliases, 'person_id')
# Independent minima over the same qualifying credits; no title-kind restriction.
query = qualified.aggregate(first_pseudonym=qualified.pseudonym.min(), first_title=qualified.title.min())
result = query.to_pyarrow().to_pylist()[0]
answer = {'answer': f"Pseudonym: {result['first_pseudonym']}; title: {result['first_title']}."}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))

if __name__ == '__main__':
    pass
