import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def read(group, table, columns, **kwargs):
    return pd.read_parquet(DATA / group / f'{table}.parquet', columns=columns, **kwargs)

def numeric_id(series):
    return pd.to_numeric(series.str.extract(r'(\d+)', expand=False), errors='raise').astype('int64')

roles = read('people', 'role_type', ['id', 'role'])
actress_roles = numeric_id(roles.loc[roles.role.eq('actress'), 'id']).tolist()
voice_notes = ['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)']
credits = read('people', 'cast_info', ['person_id', 'movie_id', 'person_role_id', 'role_id', 'note'],
               filters=[('note', 'in', voice_notes), ('role_id', 'in', actress_roles)])
credits['person_id'] = numeric_id(credits.person_id)

companies = read('movies', 'company_name', ['id', 'country_code'])
us_companies = numeric_id(companies.loc[companies.country_code.eq('[us]'), 'id'])
links = read('movies', 'movie_companies', ['movie_id', 'company_id'])
us_titles = links.loc[links.company_id.isin(us_companies), 'movie_id']
credits = credits.loc[credits.movie_id.isin(us_titles)].copy()
del companies, links

people = read('people', 'name', ['id', 'name', 'gender'], filters=[('gender', '=', 'f')])
people['person_id'] = numeric_id(people.id)
people = people[['person_id', 'name']].rename(columns={'name': 'actress_name'})
credits = credits.merge(people, on='person_id', how='inner')
del people

characters = read('people', 'char_name', ['id', 'name']).rename(columns={'id': 'person_role_id', 'name': 'character_name'})
characters = characters.loc[characters.character_name.notna()]
credits = credits.merge(characters, on='person_role_id', how='inner')
del characters

# Alternate names must belong to the very person holding the credit.
aliases = read('people', 'aka_name', ['person_id', 'name']).rename(columns={'name': 'alternate_name'})
credits = credits.merge(aliases, on='person_id', how='inner')
del aliases

# Include every title kind, as required by the task clarification.
titles = read('movies', 'title', ['id', 'title'])
titles['movie_id'] = numeric_id(titles.id)
credits = credits.merge(titles[['movie_id', 'title']], on='movie_id', how='inner')
fields = ['alternate_name', 'character_name', 'actress_name', 'title']
result = {field: credits[field].dropna().min() for field in fields}
assert len(credits) > 0
answer = '; '.join(f'{label}: {result[field]}' for label, field in zip(
    ['Alternate name', 'Character name', 'Actress name', 'Title'], fields)) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(json.dumps({'qualifying_rows': len(credits), **result}, ensure_ascii=False))
