import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
con.raw_sql("SET temp_directory='/workspace/work/duckdb_tmp'")

def load(group, name, encoded=()):
    t = con.read_parquet(f'/workspace/data/{group}/{name}.parquet', table_name=name)
    return t.mutate(**{c: t[c].re_extract(r'([0-9]+)', 1).cast('int64') for c in encoded})

t = load('movies', 'title', ['id'])
it = load('movies', 'info_type', ['id'])
mi = load('movies', 'movie_info', ['info_type_id'])
k = load('movies', 'keyword', ['id'])
mk = load('movies', 'movie_keyword', ['keyword_id'])
cn = load('movies', 'company_name', ['id'])
mc = load('movies', 'movie_companies', ['id'])
cc = load('movies', 'complete_cast')
cct = load('movies', 'comp_cast_type')
n = load('people', 'name', ['id'])
an = load('people', 'aka_name')
ci = load('people', 'cast_info', ['person_id'])
ch = load('people', 'char_name')
pi = load('people', 'person_info')
rt = load('people', 'role_type', ['id'])

# Existential requirements use semijoins to avoid multiplying duplicate records.
people = n.filter((n.gender == 'f') & n.name.contains('An'))
people = people.semi_join(an, people.id == an.person_id)
trivia = pi.semi_join(it.filter(it['info'] == 'trivia'), pi.info_type_id == it.id)
people = people.semi_join(trivia, people.id == trivia.person_id)
people = people.select(person_id=people.id, actress_name=people.name)

animated = mk.semi_join(k.filter(k.keyword == 'computer-animation'), mk.keyword_id == k.id)
us = mc.semi_join(cn.filter(cn.country_code == '[us]'), mc.company_id == cn.id)
releases = mi.semi_join(it.filter(it['info'] == 'release dates'), mi.info_type_id == it.id)
releases = releases.filter(releases['info'].like('Japan:%200%') | releases['info'].like('USA:%200%'))
complete = cc.semi_join(cct.filter(cct.kind == 'cast'), cc.subject_id == cct.id)
status = cct.view()
complete = complete.semi_join(status.filter(status.kind == 'complete+verified'), complete.status_id == status.id)
movies = t.filter(t.production_year.between(2000, 2010))
for required in (animated, us, releases, complete):
    movies = movies.semi_join(required, movies.id == required.movie_id)
movies = movies.select(movie_id=movies.id, title=movies.title)

credits = ci.filter(ci.note.isin(['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)']))
credits = credits.semi_join(rt.filter(rt.role == 'actress'), credits.role_id == rt.id)
characters = ch.select(character_id=ch.id, character_name=ch.name)
matched = credits.join(people, 'person_id').join(movies, 'movie_id').join(characters, [('person_role_id', 'character_id')])
result = matched.aggregate(character_name=matched.character_name.min(), actress_name=matched.actress_name.min(), title=matched.title.min())
(OUT / 'query.sql').write_text(ibis.to_sql(result, dialect='duckdb'))
row = result.to_pyarrow().to_pylist()[0]
assert all(v is not None for v in row.values()), 'No matching records'
answer = f"Character: {row['character_name']}; actress: {row['actress_name']}; title: {row['title']}."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(answer)

if __name__ == '__main__':
    pass
