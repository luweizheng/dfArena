import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
files = con.read_parquet('/workspace/data/artifacts/files.parquet', table_name='files')
contents = con.read_parquet('/workspace/data/artifacts/contents.parquet', table_name='contents')
languages = con.read_parquet('/workspace/data/metadata/languages.parquet', table_name='languages')
# Repository language declarations can list multiple languages.
swift_repos = languages.filter(languages.language_description.re_search(r'\bSwift\b')).select('repo_name').distinct()
# Identify blobs by files.id; repeated references must not inflate copy counts.
swift_files = files.filter(files.path.endswith('.swift')).select('id', 'repo_name', 'path').distinct()
swift_files = swift_files.semi_join(swift_repos, 'repo_name')
nonbinary = contents.filter(contents.repo_data_description.lower().contains('non-binary'))
metadata = nonbinary.select('id', copies=nonbinary.repo_data_description.re_extract(r'([0-9][0-9,]*) times', 1).replace(',', '').nullif('').cast('int64'))
metadata = metadata.group_by('id').aggregate(copies=metadata.copies.max())
candidates = swift_files.join(metadata, 'id').select(swift_files.id, swift_files.repo_name, swift_files.path, metadata.copies).distinct()
ranked = candidates.order_by(ibis.desc('copies'), 'id', 'repo_name', 'path')
rows = ranked.to_pyarrow().to_pylist()
assert rows and rows[0]['copies'] is not None
winners = [r for r in rows if r['copies'] == rows[0]['copies']]
(OUT / 'ranking.json').write_text(json.dumps(rows, indent=2))
answer = '; '.join(f"{r['repo_name']} — {r['path']} (ID: {r['id']}; {r['copies']:,} copies)" for r in winners) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps({'winners': winners, 'candidate_count': len(rows)}, indent=2))
