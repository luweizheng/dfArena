import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def read(group, table, columns):
    return pd.read_parquet(DATA / group / f'{table}.parquet', columns=columns)

def numeric_id(series):
    return pd.to_numeric(series.astype('string').str.extract(r'(\d+)', expand=False), errors='raise').astype('Int64')

def main():
    kinds = read('movies', 'kind_type', ['id', 'kind'])
    titles = read('movies', 'title', ['id', 'title', 'kind_id', 'production_year'])
    titles = titles.loc[titles.kind_id.isin(kinds.loc[kinds.kind.eq('movie'), 'id']) & titles.production_year.gt(2000)].copy()
    titles['movie_id'] = numeric_id(titles.id)

    completeness_types = read('movies', 'comp_cast_type', ['id', 'kind'])
    complete = read('movies', 'complete_cast', ['movie_id', 'subject_id', 'status_id'])
    complete = complete.loc[
        complete.subject_id.isin(completeness_types.loc[completeness_types.kind.eq('cast'), 'id'])
        & complete.status_id.isin(completeness_types.loc[completeness_types.kind.str.contains('complete', regex=False, na=False), 'id'])
    ]
    titles = titles.loc[titles.movie_id.isin(complete.movie_id)]

    tags = {'superhero', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence', 'magnet', 'web', 'claw', 'laser'}
    keywords = read('movies', 'keyword', ['id', 'keyword'])
    keyword_ids = numeric_id(keywords.loc[keywords.keyword.isin(tags), 'id'])
    movie_keywords = read('movies', 'movie_keyword', ['movie_id', 'keyword_id'])
    movie_keywords = movie_keywords.loc[movie_keywords.movie_id.isin(titles.movie_id)].copy()
    movie_keywords['keyword_id'] = numeric_id(movie_keywords.keyword_id)
    titles = titles.loc[titles.movie_id.isin(movie_keywords.loc[movie_keywords.keyword_id.isin(keyword_ids), 'movie_id'])]

    characters = read('people', 'char_name', ['id', 'name'])
    character_ids = characters.loc[characters.name.str.contains('man|Man', regex=True, na=False), 'id']
    credits = read('people', 'cast_info', ['person_id', 'movie_id', 'person_role_id'])
    credits = credits.loc[credits.movie_id.isin(titles.movie_id) & credits.person_role_id.isin(character_ids)].copy()
    credits['person_id'] = numeric_id(credits.person_id)
    names = read('people', 'name', ['id', 'name'])
    names['person_id'] = numeric_id(names.id)
    matches = credits.merge(names[['person_id', 'name']], on='person_id', how='inner').merge(titles[['movie_id', 'title']], on='movie_id', how='inner')
    assert not matches.empty, 'No qualifying cast credits'
    # Independent minima over all qualifying joined rows.
    first_name = matches['name'].dropna().min()
    first_title = matches['title'].dropna().min()
    result = {'answer': f'Cast member: {first_name}; title: {first_title}.'}
    (OUT / 'answer.json').write_text(json.dumps(result, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    print(f'Qualifying credits: {len(matches)}; movies: {matches.movie_id.nunique()}')

if __name__ == '__main__':
    main()
