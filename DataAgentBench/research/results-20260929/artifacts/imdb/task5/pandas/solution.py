import json
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data/movies')
OUT = Path('/workspace/work')
def read(name, columns=None):
    return pd.read_parquet(ROOT / f'{name}.parquet', columns=columns)
def ids(series):
    return pd.to_numeric(series.astype('string').str.extract(r'(\d+)', expand=False), errors='raise').astype('Int64')

def main():
    kinds = read('kind_type')
    roles = read('company_type')
    types = read('info_type')
    types['id'] = ids(types['id'])
    titles = read('title', ['id', 'title', 'kind_id'])
    titles = titles[titles.kind_id.isin(kinds.loc[kinds.kind.eq('movie'), 'id'])].copy()
    titles['movie_id'] = ids(titles['id'])
    companies = read('company_name', ['id', 'name', 'country_code'])
    companies = companies[companies.country_code.eq('[us]')].copy()
    companies['company_id'] = ids(companies['id'])
    links = read('movie_companies', ['movie_id', 'company_id', 'company_type_id'])
    links = links[links.company_type_id.isin(roles.loc[roles.kind.eq('production companies'), 'id'])]
    linked = links.merge(companies[['company_id', 'name']], on='company_id').merge(titles[['movie_id', 'title']], on='movie_id')
    info = read('movie_info', ['movie_id', 'info_type_id'])
    # Normalize distinct encoded type IDs once, then map every metadata row.
    lookup = pd.Series(ids(pd.Series(info.info_type_id.unique())).to_numpy(), index=info.info_type_id.unique())
    release_ids = info.loc[info.info_type_id.map(lookup).isin(types.loc[types['info'].eq('release dates'), 'id']), 'movie_id']
    linked = linked[linked.movie_id.isin(release_ids)]
    ratings = read('movie_info_idx', ['movie_id', 'info_type_id', 'info'])
    ratings = ratings[ratings.info_type_id.isin(types.loc[types['info'].eq('rating'), 'id'])]
    eligible = linked.merge(ratings[['movie_id', 'info']], on='movie_id')
    result = {label: eligible[column].dropna().min() for label, column in [('company', 'name'), ('rating', 'info'), ('title', 'title')]}
    answer = f"Company: {result['company']}; rating: {result['rating']}; title: {result['title']}."
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(answer)
    print(f'Eligible titles: {eligible.movie_id.nunique()}')

if __name__ == '__main__':
    main()
