import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def scan(group, table):
    return pl.scan_parquet(DATA / group / f'{table}.parquet')

def ident(column):
    return pl.col(column).cast(pl.String).str.replace_all(r'[^0-9]', '').cast(pl.Int64)

info = scan('movies', 'info_type').select(ident('id').alias('info_type_id'), 'info')
genre_types = info.filter(pl.col('info') == 'genres').select('info_type_id')
vote_types = info.filter(pl.col('info') == 'votes').select('info_type_id')
genres = (scan('movies', 'movie_info')
    .filter(pl.col('info').is_in(['Horror', 'Thriller']))
    .with_columns(ident('info_type_id'), pl.col('movie_id').cast(pl.Int64))
    .join(genre_types, on='info_type_id', how='semi')
    .select('movie_id', pl.col('info').alias('genre')))
votes = (scan('movies', 'movie_info_idx')
    .with_columns(pl.col('info_type_id').cast(pl.Int64), pl.col('movie_id').cast(pl.Int64))
    .join(vote_types, on='info_type_id', how='semi')
    .filter(pl.col('info').is_not_null())
    .select('movie_id', pl.col('info').alias('vote_count')))
keywords = (scan('movies', 'keyword')
    .filter(pl.col('keyword').is_in(['murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital']))
    .select(ident('id').alias('keyword_id')))
keyword_movies = (scan('movies', 'movie_keyword')
    .with_columns(ident('keyword_id'), pl.col('movie_id').cast(pl.Int64))
    .join(keywords, on='keyword_id', how='semi').select('movie_id'))
companies = (scan('movies', 'company_name')
    .filter(pl.col('name').str.contains('Lionsgate', literal=True))
    .select(ident('id').alias('company_id')))
company_movies = (scan('movies', 'movie_companies')
    .with_columns(pl.col('company_id').cast(pl.Int64), pl.col('movie_id').cast(pl.Int64))
    .join(companies, on='company_id', how='semi').select('movie_id'))
men = (scan('people', 'name').filter(pl.col('gender') == 'm')
    .select(ident('id').alias('person_id'), pl.col('name').alias('writer_name')))
# The specified writing-credit labels are stored in cast_info.note.
writers = (scan('people', 'cast_info')
    .filter(pl.col('note').is_in(['(writer)', '(head writer)', '(written by)', '(story)', '(story editor)']))
    .select('movie_id', ident('person_id'))
    .join(men, on='person_id', how='inner'))
titles = scan('movies', 'title').select(ident('id').alias('movie_id'), 'title', 'kind_id')
matched = (titles.join(keyword_movies, on='movie_id', how='semi')
    .join(company_movies, on='movie_id', how='semi')
    .join(genres, on='movie_id', how='inner')
    .join(votes, on='movie_id', how='inner')
    .join(writers, on='movie_id', how='inner').collect(engine='streaming'))
columns = ['genre', 'vote_count', 'writer_name', 'title']
result = matched.select(pl.col(c).min() for c in columns).row(0, named=True)
assert matched.height > 0
answer = (f"Genre: {result['genre']}; vote count: {result['vote_count']}; "
          f"writer: {result['writer_name']}; title: {result['title']}.")
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(answer)
print('Matching rows:', matched.height)
# Keep supporting rows for each independent minimum for reproducibility.
witnesses = pl.concat([matched.filter(pl.col(c) == result[c]).with_columns(pl.lit(c).alias('minimum_field')) for c in columns])
witnesses.write_parquet(OUT / 'minimum_witnesses.parquet')
print(witnesses.select('minimum_field', *columns, 'kind_id').unique())
