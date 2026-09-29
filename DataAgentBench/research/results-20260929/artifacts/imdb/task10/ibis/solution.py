import json
from pathlib import Path
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()

def table(group, name):
    return con.read_parquet(str(DATA / group / f'{name}.parquet'), table_name=name)

def numeric_id(column):
    return column.re_replace(r'[^0-9]', '').cast('int64')

t = table('movies', 'title')
kt = table('movies', 'kind_type')
k = table('movies', 'keyword')
mk = table('movies', 'movie_keyword')
cc = table('movies', 'complete_cast')
cct = table('movies', 'comp_cast_type')
ci = table('people', 'cast_info')
ch = table('people', 'char_name')
n = table('people', 'name')

keywords = ['superhero', 'marvel-comics', 'based-on-comic', 'tv-special',
            'fight', 'violence', 'magnet', 'web', 'claw', 'laser']
movies = t.filter(t.production_year > 2000).select(
    movie_id=numeric_id(t.id), title=t.title, kind_id=t.kind_id)
movies = movies.semi_join(kt.filter(kt.kind == 'movie'), movies.kind_id == kt.id)
keyword_ids = k.filter(k.keyword.isin(keywords)).select(keyword_id=numeric_id(k.id))
tags = mk.select(movie_id=mk.movie_id, keyword_id=numeric_id(mk.keyword_id))
tagged_movies = tags.semi_join(keyword_ids, 'keyword_id').select('movie_id')
subjects = cct.filter(cct.kind == 'cast').select(subject_id=cct.id)
statuses = cct.filter(cct.kind.contains('complete')).select(status_id=cct.id)
complete_movies = cc.semi_join(subjects, 'subject_id').semi_join(statuses, 'status_id').select('movie_id')
movies = movies.semi_join(tagged_movies, 'movie_id').semi_join(complete_movies, 'movie_id')
characters = ch.filter(ch.name.notnull() & (ch.name.contains('man') | ch.name.contains('Man'))).select(person_role_id=ch.id)
credits = ci.semi_join(characters, 'person_role_id').select(
    movie_id=ci.movie_id, person_id=numeric_id(ci.person_id))
people = n.select(person_id=numeric_id(n.id), cast_member=n.name)
matching = movies.inner_join(credits, 'movie_id').inner_join(people, 'person_id')
result = matching.aggregate(first_cast_member=matching.cast_member.min(), first_title=matching.title.min())
row = result.to_pyarrow().to_pylist()[0]
answer = {'answer': f"Cast member: {row['first_cast_member']}; title: {row['first_title']}."}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))

if __name__ == '__main__':
    pass
