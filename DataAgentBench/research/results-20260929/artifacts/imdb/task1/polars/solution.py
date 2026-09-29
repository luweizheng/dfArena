import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data/movies')
OUT = Path('/workspace/work')
def scan(name):
    return pl.scan_parquet(DATA / f'{name}.parquet')
def numeric(name):
    return pl.col(name).str.replace_all(r'[^0-9]', '').cast(pl.Int32)

kinds = scan('kind_type').filter(pl.col('kind').is_in(['movie', 'tv movie', 'video movie', 'video game'])).select(pl.col('id').alias('kind_id'), 'kind')
titles = scan('title').filter(pl.col('production_year') > 1990).select(numeric('id').alias('movie_id'), 'title', 'kind_id', 'production_year').join(kinds, on='kind_id')
companies = scan('company_name').filter(pl.col('country_code') == '[us]').select(numeric('id').alias('company_id'))
us_titles = scan('movie_companies').join(companies, on='company_id', how='semi').select('movie_id')
keywords = scan('keyword').select(numeric('id').alias('keyword_id'))
tagged = scan('movie_keyword').with_columns(numeric('keyword_id')).join(keywords, on='keyword_id', how='semi').select('movie_id')
subjects = scan('comp_cast_type').filter(pl.col('kind') == 'cast').select(pl.col('id').alias('subject_id'))
statuses = scan('comp_cast_type').filter(pl.col('kind') == 'complete+verified').select(pl.col('id').alias('status_id'))
cast = scan('complete_cast').join(subjects, on='subject_id', how='semi').join(statuses, on='status_id', how='semi').select('movie_id')
release_types = scan('info_type').filter(pl.col('info') == 'release dates').select(numeric('id').alias('info_type_id'))
releases = scan('movie_info').with_columns(numeric('info_type_id')).join(release_types, on='info_type_id', how='semi').filter(pl.col('info').str.starts_with('USA:') & pl.col('info').str.contains(r'\b(?:199[0-9]|200[0-9])\b') & pl.col('note').str.contains('(internet)', literal=True))
result = titles
for matching in [us_titles, tagged, cast, releases.select('movie_id')]:
    result = result.join(matching, on='movie_id', how='semi')
result = result.sort(['title', 'kind', 'movie_id']).collect()
result.write_csv(OUT / 'matching_titles.csv')
assert result.height, 'No matching titles'
first = result.row(0, named=True)
releases.filter(pl.col('movie_id') == first['movie_id']).collect().write_csv(OUT / 'first_title_releases.csv')
answer = {'answer': f"{first['title']} — {first['kind']}."}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))
print(result.head(10))
