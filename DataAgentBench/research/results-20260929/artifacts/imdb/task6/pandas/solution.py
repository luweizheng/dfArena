import json
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
def read(group, table, columns, filters=None):
    return pd.read_parquet(ROOT / group / (table + '.parquet'), columns=columns, filters=filters)
def decode(s):
    return pd.to_numeric(s.str.extract(r'(\d+)', expand=False), errors='raise').astype('Int64')
def lookup(table, label, group='movies', field='info'):
    d = read(group, table, ['id', field])
    ids = d.loc[d[field].eq(label), 'id']
    return decode(ids) if pd.api.types.is_object_dtype(ids.dtype) or pd.api.types.is_string_dtype(ids.dtype) else ids

# All title kinds are eligible; production bounds are inclusive.
t = read('movies', 'title', ['id', 'title', 'production_year'], [('production_year', '>=', 2000), ('production_year', '<=', 2010)])
t['movie_id'] = decode(t['id'])
k = read('movies', 'keyword', ['id', 'keyword'], [('keyword', '=', 'computer-animation')])
kids = decode(k['id'])
mk = read('movies', 'movie_keyword', ['movie_id', 'keyword_id'], [('movie_id', 'in', t.movie_id.tolist())])
mk = mk.loc[decode(mk.keyword_id).isin(kids)]
t = t[t.movie_id.isin(mk.movie_id)]
cc = read('movies', 'complete_cast', ['movie_id', 'subject_id', 'status_id'])
cc = cc[cc.subject_id.isin(lookup('comp_cast_type', 'cast', field='kind')) & cc.status_id.isin(lookup('comp_cast_type', 'complete+verified', field='kind'))]
t = t[t.movie_id.isin(cc.movie_id)]
cn = read('movies', 'company_name', ['id', 'country_code'], [('country_code', '=', '[us]')])
mc = read('movies', 'movie_companies', ['movie_id', 'company_id'], [('movie_id', 'in', t.movie_id.tolist())])
t = t[t.movie_id.isin(mc.loc[mc.company_id.isin(decode(cn.id)), 'movie_id'])]
mi = read('movies', 'movie_info', ['movie_id', 'info_type_id', 'info'], [('movie_id', 'in', t.movie_id.tolist())])
mi = mi[decode(mi.info_type_id).isin(lookup('info_type', 'release dates'))]
mi = mi[mi['info'].str.match(r'^(Japan|USA):.*200[0-9]', na=False)]
t = t[t.movie_id.isin(mi.movie_id)]
print('Eligible titles:', len(t), flush=True)

n = read('people', 'name', ['id', 'name', 'gender'], [('gender', '=', 'f')])
n = n[n['name'].str.contains('An', regex=False, na=False)].copy()
n['person_id'] = decode(n.id)
a = read('people', 'aka_name', ['person_id'])
n = n[n.person_id.isin(a.person_id)]
p = read('people', 'person_info', ['person_id', 'info_type_id'], [('person_id', 'in', n.person_id.tolist())])
n = n[n.person_id.isin(p.loc[p.info_type_id.isin(lookup('info_type', 'trivia')), 'person_id'])]
c = read('people', 'cast_info', ['person_id', 'movie_id', 'person_role_id', 'role_id', 'note'], [('movie_id', 'in', t.movie_id.tolist())])
c = c[c.role_id.isin(lookup('role_type', 'actress', group='people', field='role')) & c.note.isin(['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)'])].copy()
c['person_id'] = decode(c.person_id)
c = c.merge(n[['person_id', 'name']], on='person_id').merge(t[['movie_id', 'title']], on='movie_id')
ch = read('people', 'char_name', ['id', 'name'], [('id', 'in', c.person_role_id.dropna().astype(int).tolist())]).rename(columns={'id': 'person_role_id', 'name': 'character'})
c = c.merge(ch, on='person_role_id')
c = c[c.character.notna()]
c.to_csv(OUT / 'qualifying_credits.csv', index=False)
assert not c.empty, 'No qualifying credits'
mins = c[['character', 'name', 'title']].min()
answer = f"Character: {mins['character']}; actress: {mins['name']}; title: {mins['title']}."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(answer)
