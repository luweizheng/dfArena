import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def read(group, table, columns):
    return pd.read_parquet(DATA / group / f'{table}.parquet', columns=columns, dtype_backend='pyarrow')

def numeric_id(series):
    return series.astype('string').str.extract(r'([0-9]+)', expand=False).astype('Int64')

def main():
    keywords = read('movies', 'keyword', ['id', 'keyword'])
    target_ids = numeric_id(keywords.loc[keywords.keyword.eq('character-name-in-title'), 'id'])
    links = read('movies', 'movie_keyword', ['movie_id', 'keyword_id'])
    tagged = links.loc[numeric_id(links.keyword_id).isin(target_ids), 'movie_id'].drop_duplicates()
    del links
    companies = read('movies', 'movie_companies', ['movie_id'])
    eligible = tagged[tagged.isin(companies.movie_id)].drop_duplicates()
    del companies
    titles = read('movies', 'title', ['id'])
    eligible = eligible[eligible.isin(numeric_id(titles.id))]
    del titles
    names = read('people', 'name', ['id', 'name'])
    names = names.loc[names.name.str.startswith('Z', na=False)].copy()
    names['person_id'] = numeric_id(names.id)
    credits = read('people', 'cast_info', ['person_id', 'movie_id'])
    credits = credits.loc[credits.movie_id.isin(eligible)].copy()
    credits['person_id'] = numeric_id(credits.person_id)
    result = names.loc[names.person_id.isin(credits.person_id), 'name'].dropna().sort_values()
    if result.empty:
        raise ValueError('No matching names')
    answer = str(result.iloc[0])
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(json.dumps({'answer': answer, 'matching_names': len(result)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
