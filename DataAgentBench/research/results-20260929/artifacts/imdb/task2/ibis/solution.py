import json
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    con = ibis.duckdb.connect()
    def table(group, name):
        return con.read_parquet(str(ROOT / group / (name + '.parquet')))
    def numeric_id(col):
        return col.re_extract(r'([0-9]+)', 1).cast('int64')

    aka = table('people', 'aka_name').select('person_id', pseudonym='name')
    names_raw = table('people', 'name')
    names = names_raw.select(person_id=numeric_id(names_raw.id))
    cast_raw = table('people', 'cast_info')
    credits = cast_raw.select(person_id=numeric_id(cast_raw.person_id), movie_id=cast_raw.movie_id, role_id=cast_raw.role_id)
    roles_raw = table('people', 'role_type')
    roles = roles_raw.filter(roles_raw.role == 'writer').select(role_id=numeric_id(roles_raw.id))
    companies_raw = table('movies', 'company_name')
    companies = companies_raw.filter(companies_raw.country_code == '[us]').select(company_id=numeric_id(companies_raw.id))
    links = table('movies', 'movie_companies').select('movie_id', 'company_id')
    titles_raw = table('movies', 'title')
    titles = titles_raw.select(movie_id=numeric_id(titles_raw.id), title=titles_raw.title)

    us_movies = links.semi_join(companies, 'company_id').select('movie_id').distinct()
    writers = credits.semi_join(roles, 'role_id').semi_join(names, 'person_id').semi_join(us_movies, 'movie_id')
    qualifying = writers.join(aka, 'person_id').join(titles, 'movie_id')
    # Independent alphabetical minima across all qualifying writer/title records.
    result = qualifying.aggregate(pseudonym=qualifying.pseudonym.min(), title=qualifying.title.min())
    row = result.to_pyarrow().to_pylist()[0]
    answer = f"Pseudonym: {row['pseudonym']}; title: {row['title']}."
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
    print(answer)

if __name__ == '__main__':
    main()
