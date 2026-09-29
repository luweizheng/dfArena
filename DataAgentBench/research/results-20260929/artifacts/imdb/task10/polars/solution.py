from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def scan(group, table):
    return pl.scan_parquet(DATA / group / f'{table}.parquet')

def ident(col):
    return pl.col(col).str.extract(r'(\d+)', 1).cast(pl.Int64)

keywords = ['superhero', 'marvel-comics', 'based-on-comic', 'tv-special',
            'fight', 'violence', 'magnet', 'web', 'claw', 'laser']
kinds = scan('movies', 'kind_type').filter(pl.col('kind') == 'movie').select(pl.col('id').alias('kind_id'))
titles = (scan('movies', 'title').filter(pl.col('production_year') > 2000)
          .join(kinds, on='kind_id', how='semi')
          .select(ident('id').alias('movie_id'), 'title'))
kw = (scan('movies', 'keyword').filter(pl.col('keyword').is_in(keywords))
      .select(ident('id').alias('keyword_id')))
tagged = (scan('movies', 'movie_keyword')
          .select(pl.col('movie_id').cast(pl.Int64), ident('keyword_id'))
          .join(kw, on='keyword_id', how='semi').select('movie_id'))
types = scan('movies', 'comp_cast_type')
subjects = types.filter(pl.col('kind') == 'cast').select(pl.col('id').alias('subject_id'))
statuses = types.filter(pl.col('kind').str.contains('complete', literal=True)).select(pl.col('id').alias('status_id'))
complete = (scan('movies', 'complete_cast')
            .join(subjects, on='subject_id', how='semi')
            .join(statuses, on='status_id', how='semi')
            .select(pl.col('movie_id').cast(pl.Int64)))
movies = titles.join(tagged, on='movie_id', how='semi').join(complete, on='movie_id', how='semi')
characters = (scan('people', 'char_name')
              .filter(pl.col('name').is_not_null() & pl.col('name').str.contains('man|Man'))
              .select(pl.col('id').alias('person_role_id')))
credits = (scan('people', 'cast_info')
           .select('movie_id', 'person_role_id', ident('person_id'))
           .join(movies, on='movie_id', how='inner')
           .join(characters, on='person_role_id', how='semi'))
names = scan('people', 'name').select(ident('id').alias('person_id'), 'name')
result = (credits.join(names, on='person_id', how='inner')
          .select(pl.col('name').min().alias('first_cast_member'),
                  pl.col('title').min().alias('first_title'), pl.len().alias('qualifying_credits'))
          .collect(engine='streaming').row(0, named=True))
assert result['qualifying_credits'] > 0
answer = {'answer': f"Cast member: {result['first_cast_member']}; title: {result['first_title']}."}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(result, ensure_ascii=False))
print(json.dumps(answer, ensure_ascii=False))

if __name__ == '__main__':
    pass
