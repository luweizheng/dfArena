import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data/movies')
OUT = Path('/workspace/work')
def read(table, columns=None):
    return pd.read_parquet(DATA / f'{table}.parquet', columns=columns)
def ids(s):
    return pd.to_numeric(s.str.extract(r'(\d+)', expand=False), errors='raise').astype('Int64')

kinds = read('kind_type')
titles = read('title', ['id', 'title', 'kind_id', 'production_year'])
titles = titles.loc[titles.production_year.gt(1990) & titles.kind_id.isin(kinds.loc[kinds.kind.isin(['movie','tv movie','video movie','video game']), 'id'])].copy()
titles['id'] = ids(titles.id)

cast_types = read('comp_cast_type')
cast = read('complete_cast')
cast = cast.loc[cast.subject_id.isin(cast_types.loc[cast_types.kind.eq('cast'), 'id']) & cast.status_id.isin(cast_types.loc[cast_types.kind.eq('complete+verified'), 'id'])]
titles = titles.loc[titles.id.isin(cast.movie_id)]

companies = read('company_name', ['id', 'country_code'])
us_ids = ids(companies.loc[companies.country_code.eq('[us]'), 'id'])
links = read('movie_companies', ['movie_id', 'company_id'])
titles = titles.loc[titles.id.isin(links.loc[links.company_id.isin(us_ids), 'movie_id'])]

keywords = read('keyword', ['id'])
keyword_links = read('movie_keyword', ['movie_id', 'keyword_id'])
keyword_links = keyword_links.loc[keyword_links.movie_id.isin(titles.id)].copy()
keyword_links['keyword_id'] = ids(keyword_links.keyword_id)
titles = titles.loc[titles.id.isin(keyword_links.loc[keyword_links.keyword_id.isin(ids(keywords.id)), 'movie_id'])]

info_types = read('info_type')
release_type_ids = ids(info_types.loc[info_types['info'].eq('release dates'), 'id'])
info = read('movie_info', ['movie_id', 'info_type_id', 'info', 'note'])
info = info.loc[info.movie_id.isin(titles.id)].copy()
info['info_type_id'] = ids(info.info_type_id)
releases = info.loc[info.info_type_id.isin(release_type_ids)]
# Release country and year are encoded in info; release medium is in note.
releases = releases.loc[releases['info'].str.match(r'^USA:.*\b(?:199\d|200\d)\b', na=False) & releases.note.str.contains('(internet)', regex=False, na=False)]
result = titles.loc[titles.id.isin(releases.movie_id)].merge(kinds, left_on='kind_id', right_on='id', suffixes=('', '_kind')).sort_values('title')
assert not result.empty, 'No matching titles'
first = result.iloc[0]
answer = {'answer': f'{first["title"]} — {first["kind"]}.'}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(result[['title','kind','production_year']].head(10).to_string(index=False))
print(releases.loc[releases.movie_id.eq(first['id'])].to_string(index=False))
print(json.dumps(answer, ensure_ascii=False))
