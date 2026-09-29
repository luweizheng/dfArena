import json
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data/movies')
OUT = Path('/workspace/work')

def table(name):
    return pl.scan_parquet(ROOT / f'{name}.parquet')

def numeric_id(name):
    return pl.col(name).str.replace_all(r'[^0-9]', '').cast(pl.Int64)

def main():
    kinds = table('kind_type').filter(pl.col('kind') == 'movie').select(pl.col('id').alias('kind_id'))
    roles = table('company_type').filter(pl.col('kind') == 'production companies').select(pl.col('id').alias('company_type_id'))
    info_types = table('info_type').with_columns(numeric_id('id'))
    release_types = info_types.filter(pl.col('info') == 'release dates').select(pl.col('id').alias('info_type_id'))
    rating_types = info_types.filter(pl.col('info') == 'rating').select(pl.col('id').alias('info_type_id'))
    titles = table('title').join(kinds, on='kind_id', how='semi').select(numeric_id('id').alias('movie_id'), 'title')
    releases = (table('movie_info').with_columns(numeric_id('info_type_id'))
                .join(release_types, on='info_type_id', how='semi')
                .filter(pl.col('info').is_not_null()).select('movie_id'))
    ratings = (table('movie_info_idx').with_columns(pl.col('info_type_id').cast(pl.Int64))
               .join(rating_types, on='info_type_id', how='semi')
               .filter(pl.col('info').is_not_null()).select('movie_id', pl.col('info').alias('rating')))
    companies = table('company_name').filter(pl.col('country_code') == '[us]').select(numeric_id('id').alias('company_id'), pl.col('name').alias('company'))
    associations = (table('movie_companies').join(roles, on='company_type_id', how='semi')
                    .join(companies, on='company_id').select('movie_id', 'company'))
    qualifying = (titles.join(releases, on='movie_id', how='semi')
                  .join(ratings, on='movie_id').join(associations, on='movie_id'))
    # Independent lexical minima; rating remains a string.
    result = qualifying.select(pl.col('company').min(), pl.col('rating').min(), pl.col('title').min(), pl.len().alias('qualifying_rows')).collect(engine='streaming').row(0, named=True)
    assert result['qualifying_rows'] > 0
    answer = f"Company: {result['company']}; rating: {result['rating']}; title: {result['title']}."
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
