import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def read(group, table, columns, filters=None):
    return pd.read_parquet(DATA / group / (table + '.parquet'), columns=columns, filters=filters)

def numeric(s):
    return pd.to_numeric(s.str.replace(r'[^0-9]', '', regex=True), errors='raise').astype('int64')

def main():
    roles = read('people', 'role_type', ['id','role'])
    actress_ids = numeric(roles.loc[roles.role.eq('actress'), 'id']).tolist()
    voice_notes = ['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)']
    cast = read('people', 'cast_info', ['person_id','movie_id','person_role_id','note','role_id'], [('role_id','in',actress_ids), ('note','in',voice_notes)])
    cast['person_id'] = numeric(cast.person_id)
    names = read('people', 'name', ['id','name','gender'], [('gender','=','f')])
    names['person_id'] = numeric(names.id)
    alternate = read('people', 'aka_name', ['person_id'])
    names = names[names.person_id.isin(alternate.person_id)]
    cast = cast.merge(names[['person_id','name']], on='person_id', how='inner')
    chars = read('people', 'char_name', ['id','name'])
    cast = cast[cast.person_role_id.isin(chars.loc[chars.name.notna(), 'id'])]
    titles = read('movies', 'title', ['id','title','production_year'], [('production_year','>',2000)])
    titles['movie_id'] = numeric(titles.id)
    companies = read('movies', 'company_name', ['id','country_code'], [('country_code','=','[us]')])
    company_ids = numeric(companies.id)
    associations = read('movies', 'movie_companies', ['movie_id','company_id'])
    titles = titles[titles.movie_id.isin(associations.loc[associations.company_id.isin(company_ids), 'movie_id'])]
    info_types = read('movies', 'info_type', ['id','info'])
    release_ids = numeric(info_types.loc[info_types['info'].eq('release dates'), 'id'])
    # Normalize distinct encoded metadata IDs once, then map the full column.
    info = read('movies', 'movie_info', ['movie_id','info_type_id'])
    unique_ids = pd.Series(info.info_type_id.unique())
    mapping = dict(zip(unique_ids, numeric(unique_ids)))
    release_movies = info.loc[info.info_type_id.map(mapping).isin(release_ids), 'movie_id']
    titles = titles[titles.movie_id.isin(release_movies)]
    result = cast.merge(titles[['movie_id','title']], on='movie_id', how='inner')
    assert not result.empty, 'No eligible credits'
    # The two alphabetical minima are independent over all qualifying credits.
    actress = result['name'].dropna().min()
    title = result['title'].dropna().min()
    answer = {'answer': f'Actress: {actress}; title: {title}.'}
    (OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
    print(json.dumps(answer, ensure_ascii=False))
    print(f'Eligible credits: {len(result)}')

if __name__ == '__main__':
    main()
