import json
from pathlib import Path
import ibis

DATA = Path('/workspace/data/movies')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()

def table(name):
    return con.read_parquet(str(DATA / f'{name}.parquet'), table_name=name)

def numeric_id(column):
    return column.re_replace(r'[^0-9]', '').cast('int64')

t = table('title')
k = table('kind_type')
it = table('info_type')
mi = table('movie_info')
ri = table('movie_info_idx')
mc = table('movie_companies')
cn = table('company_name')
ct = table('company_type')

info_types = it.select(type_id=numeric_id(it.id), category=it['info'])
release_types = info_types.filter(info_types.category == 'release dates')
rating_types = info_types.filter(info_types.category == 'rating')
movies = t.filter(t.kind_id.isin(k.filter(k.kind == 'movie').id)).select(
    movie_id=numeric_id(t.id), title=t.title
)
release_records = mi.filter(
    numeric_id(mi.info_type_id).isin(release_types.type_id) & mi['info'].notnull()
).select('movie_id')
ratings = ri.filter(
    ri.info_type_id.isin(rating_types.type_id) & ri['info'].notnull()
).select('movie_id', rating=ri['info'])
companies = cn.filter(cn.country_code == '[us]').select(
    company_id=numeric_id(cn.id), company_name=cn.name
)
production_links = mc.filter(
    mc.company_type_id.isin(ct.filter(ct.kind == 'production companies').id)
).select('movie_id', 'company_id')
qualified = (movies.semi_join(release_records, 'movie_id')
    .join(ratings, 'movie_id')
    .join(production_links, 'movie_id')
    .join(companies, 'company_id'))
# Independent lexicographic minima, with rating retained as text.
result = qualified.aggregate(
    company_name=qualified.company_name.min(),
    rating=qualified.rating.min(),
    title=qualified.title.min(),
)
row = result.to_pyarrow().to_pylist()[0]
answer = f"Company: {row['company_name']}; rating: {row['rating']}; title: {row['title']}."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(answer)

if __name__ == '__main__':
    pass
