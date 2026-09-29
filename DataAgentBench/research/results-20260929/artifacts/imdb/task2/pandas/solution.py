import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')

def read(group, table, columns, **kwargs):
    return pd.read_parquet(DATA / group / f'{table}.parquet', columns=columns, **kwargs)

def numeric_id(series):
    return pd.to_numeric(series.astype('string').str.extract(r'(\d+)', expand=False), errors='raise').astype('Int64')

roles = read('people', 'role_type', ['id', 'role'])
writer_ids = numeric_id(roles.loc[roles['role'].eq('writer'), 'id']).tolist()
companies = read('movies', 'company_name', ['id', 'country_code'])
us_ids = numeric_id(companies.loc[companies['country_code'].eq('[us]'), 'id'])
links = read('movies', 'movie_companies', ['movie_id', 'company_id'])
us_movies = links.loc[links.company_id.isin(us_ids), 'movie_id'].drop_duplicates()
titles = read('movies', 'title', ['id', 'title'])
titles['movie_id'] = numeric_id(titles.pop('id'))
titles = titles.loc[titles.movie_id.isin(us_movies)]
credits = read('people', 'cast_info', ['person_id', 'movie_id', 'role_id'], filters=[('role_id', 'in', writer_ids)])
credits = credits.loc[credits.movie_id.isin(titles.movie_id)].copy()
credits['person_id'] = numeric_id(credits.person_id)
aliases = read('people', 'aka_name', ['person_id', 'name'])
# A registered pseudonym is an entry in aka_name. Compute independent
# minima over all qualifying writer/pseudonym/title combinations.
qualified = credits.merge(aliases, on='person_id', how='inner').merge(titles, on='movie_id', how='inner')
assert not qualified.empty
pseudonym = qualified['name'].dropna().min()
title = qualified['title'].dropna().min()
answer = {'answer': f'Pseudonym: {pseudonym}; title: {title}.'}
Path('/workspace/work/answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))
print(f'Qualifying joined rows: {len(qualified)}')
