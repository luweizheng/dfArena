import json
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
con.raw_sql("SET temp_directory='/workspace/work/duckdb_tmp'")

def table(group, name):
    return con.read_parquet(str(ROOT / group / f'{name}.parquet'), table_name=name)

def numeric_id(column):
    return column.re_replace(r'[^0-9]', '').cast('int64')

n = table('people', 'name')
a = table('people', 'aka_name')
c = table('people', 'cast_info')
r = table('people', 'role_type')
ch = table('people', 'char_name')
t = table('movies', 'title')
mc = table('movies', 'movie_companies')
cn = table('movies', 'company_name')

people = n.filter(n.gender == 'f').select(person_id=numeric_id(n.id), actress_name=n.name)
aliases = a.select(person_id=a.person_id, alternate_name=a.name)
roles = r.filter(r.role == 'actress').select(role_id=numeric_id(r.id))
voice_notes = ['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)']
credits = c.filter(c.note.isin(voice_notes)).select(
    person_id=numeric_id(c.person_id), movie_id=c.movie_id,
    character_id=c.person_role_id, role_id=c.role_id)
characters = ch.select(character_id=ch.id, character_name=ch.name)
titles = t.select(movie_id=numeric_id(t.id), title=t.title)
us_companies = cn.filter(cn.country_code == '[us]').select(company_id=numeric_id(cn.id))
us_movies = mc.semi_join(us_companies, 'company_id').select('movie_id')

# Each alternate name is joined to the person holding the qualifying credit.
# All title types are eligible. Each requested minimum is independent.
qualified = (credits.semi_join(roles, 'role_id')
             .join(people, 'person_id')
             .join(aliases, 'person_id')
             .join(characters, 'character_id')
             .join(titles, 'movie_id')
             .semi_join(us_movies, 'movie_id'))
result = qualified.aggregate(
    alternate_name=qualified.alternate_name.min(),
    character_name=qualified.character_name.min(),
    actress_name=qualified.actress_name.min(),
    title=qualified.title.min(),
)
row = result.to_pyarrow().to_pylist()[0]
answer = (f"Alternate name: {row['alternate_name']}; character name: {row['character_name']}; "
          f"actress name: {row['actress_name']}; title: {row['title']}.")
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(json.dumps(row, ensure_ascii=False))
