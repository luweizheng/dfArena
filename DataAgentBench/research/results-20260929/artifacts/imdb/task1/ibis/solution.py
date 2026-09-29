import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()

def table(name):
    return con.read_parquet(f'/workspace/data/movies/{name}.parquet', table_name=name)

def numeric(col):
    return col.re_extract(r'([0-9]+)', 1).cast('int64')

t = table('title')
t = t.mutate(movie_id=numeric(t.id))
k = table('kind_type')
t = t.filter(t.production_year > 1990).join(k, t.kind_id == k.id).select('movie_id', 'title', 'kind')
t = t.filter(t.kind.isin(['movie', 'tv movie', 'video movie', 'video game']))

kw = table('keyword')
mk = table('movie_keyword')
tagged = mk.semi_join(kw, numeric(mk.keyword_id) == numeric(kw.id)).select('movie_id')
cn = table('company_name')
cn = cn.filter(cn.country_code == '[us]')
mc = table('movie_companies')
us_company = mc.semi_join(cn, mc.company_id == numeric(cn.id)).select('movie_id')

it = table('info_type')
it = it.filter(it['info'] == 'release dates')
mi = table('movie_info')
release = mi.semi_join(it, numeric(mi.info_type_id) == numeric(it.id))
# Release dates are country-prefixed free text, with the release medium in note.
release = release.filter(
    release['info'].re_search(r'^USA:.*\b(199[0-9]|200[0-9])\b'),
    release.note.contains('internet'),
).select('movie_id')

ct = table('comp_cast_type')
subject = ct.filter(ct.kind == 'cast')
status = ct.filter(ct.kind == 'complete+verified').view()
cc = table('complete_cast')
verified = cc.semi_join(subject, cc.subject_id == subject.id)
verified = verified.semi_join(status, verified.status_id == status.id).select('movie_id')

for requirement in [tagged, us_company, release, verified]:
    t = t.semi_join(requirement, 'movie_id')
result = t.select('title', 'kind').distinct().order_by('title', 'kind').limit(1)
rows = result.to_pyarrow().to_pylist()
if not rows:
    raise ValueError('No qualifying title found')
row = rows[0]
answer = {'answer': f"{row['title']} ({row['kind']})"}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))
