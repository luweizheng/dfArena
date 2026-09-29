import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def read(group, table, columns, filters=None):
    return pd.read_parquet(DATA / group / f'{table}.parquet', columns=columns, filters=filters)

def ids(series):
    return pd.to_numeric(series.astype('string').str.extract(r'(\d+)', expand=False), errors='raise').astype('int64')

# Every eligibility condition is linked through the same numeric movie ID.
companies = read('movies', 'company_name', ['id', 'name'])
company_ids = ids(companies.loc[companies['name'].str.contains('Lionsgate', regex=False, na=False), 'id'])
mc = read('movies', 'movie_companies', ['movie_id', 'company_id'])
movie_ids = mc.loc[mc.company_id.isin(company_ids), 'movie_id'].unique().tolist()
del companies, mc

info_types = read('movies', 'info_type', ['id', 'info'])
info_types['id'] = ids(info_types.id)
genre_types = info_types.loc[info_types['info'].eq('genres'), 'id']
vote_types = info_types.loc[info_types['info'].eq('votes'), 'id']
genres = read('movies', 'movie_info', ['movie_id', 'info_type_id', 'info'], [('movie_id', 'in', movie_ids), ('info', 'in', ['Horror', 'Thriller'])])
genres['info_type_id'] = ids(genres.info_type_id)
genres = genres.loc[genres.info_type_id.isin(genre_types), ['movie_id', 'info']].rename(columns={'info': 'genre'})
movie_ids = genres.movie_id.unique().tolist()

keywords = read('movies', 'keyword', ['id', 'keyword'])
keyword_ids = ids(keywords.loc[keywords.keyword.isin(['murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital']), 'id'])
mk = read('movies', 'movie_keyword', ['movie_id', 'keyword_id'], [('movie_id', 'in', movie_ids)])
mk['keyword_id'] = ids(mk.keyword_id)
movie_ids = mk.loc[mk.keyword_id.isin(keyword_ids), 'movie_id'].unique().tolist()

votes = read('movies', 'movie_info_idx', ['movie_id', 'info_type_id', 'info'], [('movie_id', 'in', movie_ids)])
votes = votes.loc[votes.info_type_id.isin(vote_types) & votes['info'].notna(), ['movie_id', 'info']].rename(columns={'info': 'vote_count'})
movie_ids = votes.movie_id.unique().tolist()

roles = read('people', 'role_type', ['id', 'role'])
role_ids = ids(roles.loc[roles.role.isin(['writer', 'head writer', 'written by', 'story', 'story editor']), 'id'])
credits = read('people', 'cast_info', ['person_id', 'movie_id', 'role_id'], [('movie_id', 'in', movie_ids), ('role_id', 'in', role_ids.tolist())])
credits['person_id'] = ids(credits.person_id)
names = read('people', 'name', ['id', 'name', 'gender'], [('gender', '==', 'm')])
names['person_id'] = ids(names.id)
writers = credits.merge(names[['person_id', 'name']], on='person_id', how='inner')
del names

titles = read('movies', 'title', ['id', 'title', 'kind_id'])
titles['movie_id'] = ids(titles.id)
matched = writers.merge(genres, on='movie_id').merge(votes, on='movie_id').merge(titles[['movie_id', 'title', 'kind_id']], on='movie_id')
assert not matched.empty
# Independent lexical minima, including vote counts in their preserved text form.
result = {col: matched[col].dropna().min() for col in ['genre', 'vote_count', 'name', 'title']}
answer = f"Genre: {result['genre']}; vote count: {result['vote_count']}; writer: {result['name']}; title: {result['title']}."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(answer)
print('Matching movies:', matched.movie_id.nunique())
print('Title kinds:', matched.groupby('kind_id').movie_id.nunique().to_dict())
print('Movie-kind-only minima:', {col: matched.loc[matched.kind_id.eq(1), col].dropna().min() for col in result})
matched.to_csv(OUT / 'matched_records.csv', index=False)
