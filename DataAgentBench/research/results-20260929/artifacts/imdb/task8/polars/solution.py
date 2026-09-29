import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def scan(group, table):
    return pl.scan_parquet(DATA / group / f'{table}.parquet')

def numeric_id(column):
    return pl.col(column).str.extract(r'(\d+)', 1).cast(pl.Int64)

def main():
    roles = scan('people', 'role_type').filter(pl.col('role') == 'actress').select(numeric_id('id').alias('role_id'))
    people = scan('people', 'name').filter(pl.col('gender') == 'f').select(numeric_id('id').alias('person_id'), pl.col('name').alias('actress_name'))
    aliases = scan('people', 'aka_name').select('person_id', pl.col('name').alias('alternate_name'))
    characters = scan('people', 'char_name').select(pl.col('id').alias('person_role_id'), pl.col('name').alias('character_name'))
    companies = scan('movies', 'company_name').filter(pl.col('country_code') == '[us]').select(numeric_id('id').alias('company_id'))
    us_titles = scan('movies', 'movie_companies').select(pl.col('company_id').cast(pl.Int64), pl.col('movie_id').cast(pl.Int64)).join(companies, on='company_id', how='semi').select('movie_id').unique()
    # All title kinds are eligible, including series and episodes.
    titles = scan('movies', 'title').select(numeric_id('id').alias('movie_id'), 'title')
    voice_notes = ['(voice)', '(voice) (uncredited)', '(voice: Japanese version)', '(voice: English version)']
    credits = scan('people', 'cast_info').filter(pl.col('note').is_in(voice_notes)).select(numeric_id('person_id').alias('person_id'), 'movie_id', 'person_role_id', 'role_id')
    eligible = (credits.join(roles, on='role_id', how='semi')
        .join(people, on='person_id')
        .join(aliases, on='person_id')
        .join(characters, on='person_role_id')
        .filter(pl.col('character_name').is_not_null())
        .join(us_titles, on='movie_id', how='semi')
        .join(titles, on='movie_id'))
    fields = ['alternate_name', 'character_name', 'actress_name', 'title']
    result = eligible.select(pl.len().alias('qualifying_rows'), *[pl.col(c).min() for c in fields]).collect()
    row = result.row(0, named=True)
    assert row['qualifying_rows'] > 0
    answer = '; '.join(f'{label}: {row[col]}' for label, col in zip(['Alternate name', 'Character name', 'Actress name', 'Title'], fields)) + '.'
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(result)
    print(answer)

if __name__ == '__main__':
    main()
