from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
files = pl.scan_parquet(DATA / 'artifacts/files.parquet')
# Require each qualifying blob ID to identify exactly one files-table record.
unique_ids = files.group_by('id').len().filter(pl.col('len') == 1).select('id')
swift_repos = (
    pl.scan_parquet(DATA / 'metadata/languages.parquet')
    .filter(pl.col('language_description').str.contains(r'\bSwift\b'))
    .select('repo_name').unique()
)
contents = (
    pl.scan_parquet(DATA / 'artifacts/contents.parquet')
    .select('id', 'repo_data_description')
    .filter(pl.col('repo_data_description').str.contains(r'(?i)non-binary'))
    .with_columns(
        pl.col('repo_data_description').str.extract(r'(\d[\d,]*) times', 1)
        .str.replace_all(',', '').cast(pl.Int64).alias('copies')
    )
)
candidates = (
    files.filter(pl.col('path').str.ends_with('.swift'))
    .join(unique_ids, on='id', how='semi')
    .join(swift_repos, on='repo_name', how='semi')
    .join(contents, on='id', how='inner')
    .select('repo_name', 'path', 'id', 'copies').unique()
    .sort(['copies', 'repo_name', 'path'], descending=[True, False, False])
    .collect()
)
assert candidates.height > 0, 'No matching files'
assert candidates['copies'].null_count() == 0, 'Unparsed copy counts'
winners = candidates.filter(pl.col('copies') == candidates['copies'].max())
candidates.write_csv(OUT / 'candidates.csv')
answer = '; '.join(
    f"{r['repo_name']} — {r['path']} (ID: {r['id']}; {r['copies']} copies)"
    for r in winners.to_dicts()
) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(answer)
