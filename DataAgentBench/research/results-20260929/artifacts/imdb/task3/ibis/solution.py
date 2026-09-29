import json
from pathlib import Path
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
con.raw_sql("SET temp_directory='/workspace/work/duckdb_tmp'")

def read(group, table):
    return con.read_parquet(str(DATA / group / f'{table}.parquet'), table_name=table)

def numeric_id(col):
    return col.re_extract(r'([0-9]+)', 1).cast('int64')

t = read('movies', 'title')
t = t.filter(t.production_year > 2000).select(movie_id=numeric_id(t.id), title=t.title)
n = read('people', 'name')
n = n.filter(n.gender == 'f').select(person_id=numeric_id(n.id), actress=n.name)
a = read('people', 'aka_name')
n = n.semi_join(a, n.person_id == a.person_id)
r = read('people', 'role_type')
r = r.filter(r.role == 'actress').select(role_id=numeric_id(r.id))
c = read('people', 'cast_info')
c = c.filter(c.note.isin(['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)']))
c = c.select(person_id=numeric_id(c.person_id), movie_id=c.movie_id, person_role_id=c.person_role_id, role_id=c.role_id)
c = c.semi_join(r, 'role_id')
ch = read('people', 'char_name')
c = c.semi_join(ch, c.person_role_id == ch.id)
cn = read('movies', 'company_name')
cn = cn.filter(cn.country_code == '[us]').select(company_id=numeric_id(cn.id))
mc = read('movies', 'movie_companies')
mc = mc.semi_join(cn, 'company_id')
t = t.semi_join(mc, 'movie_id')
it = read('movies', 'info_type')
it = it.filter(it['info'] == 'release dates').select(info_type_id=numeric_id(it.id))
mi = read('movies', 'movie_info')
mi = mi.select(movie_id=mi.movie_id, info_type_id=numeric_id(mi.info_type_id))
mi = mi.semi_join(it, 'info_type_id')
t = t.semi_join(mi, 'movie_id')
qualified = c.join(n, 'person_id').join(t, 'movie_id')
# Each requested alphabetical first is an independent minimum over qualifying credits.
result = qualified.aggregate(actress=qualified.actress.min(), title=qualified.title.min())
row = result.to_pyarrow().to_pylist()[0]
assert row['actress'] is not None and row['title'] is not None
answer = {'answer': f"Actress: {row['actress']}; title: {row['title']}."}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))

if __name__ == '__main__':
    pass
