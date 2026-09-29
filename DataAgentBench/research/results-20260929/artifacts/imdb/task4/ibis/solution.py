import json
from pathlib import Path
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
con.raw_sql("SET temp_directory='/workspace/work/duckdb_tmp'")

def table(group, name):
    return con.read_parquet(str(DATA / group / f'{name}.parquet'))

def numeric_id(column):
    return column.re_extract(r'([0-9]+)', 1).cast('int64')

names = table('people', 'name')
names = names.filter(names.name.startswith('Z')).select(person_id=numeric_id(names.id), name=names.name)
credits = table('people', 'cast_info')
credits = credits.select(person_id=numeric_id(credits.person_id), movie_id=credits.movie_id)
keywords = table('movies', 'keyword')
keywords = keywords.filter(keywords.keyword == 'character-name-in-title').select(keyword_id=numeric_id(keywords.id))
movie_keywords = table('movies', 'movie_keyword')
movie_keywords = movie_keywords.select(movie_id=movie_keywords.movie_id, keyword_id=numeric_id(movie_keywords.keyword_id))
companies = table('movies', 'movie_companies')
titles = table('movies', 'title')
titles = titles.select(movie_id=numeric_id(titles.id))
# Movie associations are existence conditions; semijoins avoid multiplying credits.
eligible = movie_keywords.semi_join(keywords, 'keyword_id').semi_join(companies, 'movie_id').semi_join(titles, 'movie_id')
matching_credits = credits.semi_join(eligible, 'movie_id')
result = names.semi_join(matching_credits, 'person_id').select('name').order_by('name').limit(1)
rows = result.to_pyarrow().to_pylist()
if not rows:
    raise RuntimeError('No matching name found')
answer = {'answer': rows[0]['name']}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))

if __name__ == '__main__':
    pass
