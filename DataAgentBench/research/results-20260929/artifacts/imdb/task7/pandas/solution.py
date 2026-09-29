import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')

def read(group, table, columns):
    return pd.read_parquet(DATA / group / f'{table}.parquet', columns=columns)

def numeric_id(series):
    return pd.to_numeric(series.str.extract(r'(\d+)', expand=False), errors='raise').astype('Int64')

def main():
    keywords = read('movies', 'keyword', ['id', 'keyword'])
    keyword_ids = numeric_id(keywords.loc[keywords.keyword.eq('character-name-in-title'), 'id'])
    movie_keywords = read('movies', 'movie_keyword', ['movie_id', 'keyword_id'])
    movie_keywords['keyword_id'] = numeric_id(movie_keywords['keyword_id'])
    tagged_movies = movie_keywords.loc[movie_keywords.keyword_id.isin(keyword_ids), 'movie_id']
    del movie_keywords

    companies = read('movies', 'company_name', ['id', 'country_code'])
    us_ids = numeric_id(companies.loc[companies.country_code.eq('[us]'), 'id'])
    associations = read('movies', 'movie_companies', ['movie_id', 'company_id'])
    eligible_ids = associations.loc[associations.company_id.isin(us_ids) & associations.movie_id.isin(tagged_movies), 'movie_id'].drop_duplicates()
    del associations

    titles = read('movies', 'title', ['id', 'title'])
    titles['movie_id'] = numeric_id(titles['id'])
    titles = titles.loc[titles.movie_id.isin(eligible_ids), ['movie_id', 'title']]
    credits = read('people', 'cast_info', ['person_id', 'movie_id'])
    credits = credits.loc[credits.movie_id.isin(titles.movie_id)].copy()
    credits['person_id'] = numeric_id(credits.person_id)
    aliases = read('people', 'aka_name', ['person_id', 'name'])
    matched = credits.merge(aliases, on='person_id', how='inner').merge(titles, on='movie_id', how='inner')
    assert not matched.empty
    pseudonym = matched['name'].dropna().min()
    title = matched['title'].dropna().min()
    result = {'answer': f'Pseudonym: {pseudonym}; title: {title}.'}
    Path('/workspace/work/answer.json').write_text(json.dumps(result, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    print(f'Qualifying titles: {matched.movie_id.nunique()}; people: {matched.person_id.nunique()}')

if __name__ == '__main__':
    main()
