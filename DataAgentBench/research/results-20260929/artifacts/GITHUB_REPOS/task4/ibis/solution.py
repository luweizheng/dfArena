import json
from pathlib import Path
import ibis
import ibis.expr.datatypes as dt

@ibis.udf.scalar.builtin
def regexp_extract_all(value: str, pattern: str, group: int) -> list[str]:
    ...

con = ibis.duckdb.connect()
languages = con.read_parquet('/workspace/data/metadata/languages.parquet')
commits = con.read_parquet('/workspace/data/artifacts/commits.parquet')
# Extract all stated byte counts and compare Python's bytes with the maximum.
counts = regexp_extract_all(languages.language_description, r'\(([0-9,]+) bytes\)', 1)
maximum = counts.map(lambda x: x.replace(',', '').cast('int64')).sort()[-1]
python_text = languages.language_description.re_extract(r'\bPython \(([0-9,]+) bytes\)', 1)
python_bytes = python_text.nullif('').replace(',', '').cast('int64').fill_null(-1)
eligible = languages.filter(maximum.notnull() & (python_bytes < maximum)).select('repo_name').distinct()
ranked = (commits.group_by('repo_name').aggregate(commit_count=commits.count())
          .inner_join(eligible, 'repo_name')
          .order_by(ibis.desc('commit_count'), 'repo_name')
          .select('repo_name', 'commit_count').limit(5))
rows = ranked.to_pyarrow().to_pylist()
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': ', '.join(row['repo_name'] for row in rows)}))
print(json.dumps(rows, indent=2))
