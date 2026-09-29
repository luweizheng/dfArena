import json
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
con.raw_sql("SET temp_directory='/workspace/work/duckdb_tmp'")

def table(group, name):
    return con.read_parquet(str(ROOT / group / (name + '.parquet')), table_name=name)

def ident(col):
    return col.re_replace(r'[^0-9]', '').cast('int64')

it = table('movies', 'info_type')
it = it.select(type_id=ident(it.id), category=it['info'])
mi = table('movies', 'movie_info')
mi = mi.select('movie_id', type_id=ident(mi.info_type_id), genre=mi['info'])
genres = mi.join(it, 'type_id').filter(lambda t: (t.category == 'genres') & t.genre.isin(['Horror', 'Thriller'])).select('movie_id', 'genre')
idx = table('movies', 'movie_info_idx')
idx = idx.select('movie_id', type_id=idx.info_type_id.cast('int64'), votes=idx['info'])
votes = idx.join(it, 'type_id').filter(lambda t: (t.category == 'votes') & t.votes.notnull()).select('movie_id', 'votes')
k = table('movies', 'keyword')
k = k.filter(k.keyword.isin(['murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital'])).select(keyword_id=ident(k.id))
mk = table('movies', 'movie_keyword')
mk = mk.select('movie_id', keyword_id=ident(mk.keyword_id))
keywords = mk.semi_join(k, 'keyword_id').select('movie_id')
c = table('movies', 'company_name')
c = c.filter(c.name.contains('Lionsgate')).select(company_id=ident(c.id))
mc = table('movies', 'movie_companies')
companies = mc.semi_join(c, 'company_id').select('movie_id')
n = table('people', 'name')
n = n.filter(n.gender == 'm').select(person_id=ident(n.id), writer=n.name)
r = table('people', 'role_type')
r = r.filter(r.role.isin(['writer', 'head writer', 'written by', 'story', 'story editor'])).select(role_id=ident(r.id))
ci = table('people', 'cast_info')
ci = ci.select('movie_id', 'role_id', person_id=ident(ci.person_id))
writers = ci.semi_join(r, 'role_id').join(n, 'person_id').select('movie_id', 'writer')
t = table('movies', 'title')
t = t.select(movie_id=ident(t.id), title=t.title)
qualified = t.semi_join(keywords, 'movie_id').semi_join(companies, 'movie_id').join(genres, 'movie_id').join(votes, 'movie_id').join(writers, 'movie_id')
# Independent lexicographic minima, including votes as stored text.
result = qualified.aggregate(genre=qualified.genre.min(), vote_count=qualified.votes.min(), writer=qualified.writer.min(), title=qualified.title.min())
row = result.to_pyarrow().to_pylist()[0]
answer = f"Genre: {row['genre']}; vote count: {row['vote_count']}; writer: {row['writer']}; title: {row['title']}."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(json.dumps(row, ensure_ascii=False))
