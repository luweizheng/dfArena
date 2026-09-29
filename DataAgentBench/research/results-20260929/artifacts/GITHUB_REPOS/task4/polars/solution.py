import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

# Count commit records before joining to repository-level language metadata.
counts = (
    pl.scan_parquet(DATA / 'artifacts/commits.parquet')
    .group_by('repo_name')
    .agg(pl.len().alias('commit_count'))
)
repos = (
    pl.scan_parquet(DATA / 'metadata/languages.parquet')
    .join(counts, on='repo_name', how='inner')
    .with_columns(
        pl.col('language_description')
        .str.extract_all(r'\([0-9,]+ bytes\)')
        .list.eval(pl.element().str.replace_all(r'[^0-9]', '').cast(pl.UInt64))
        .list.max().alias('largest_language_bytes'),
        pl.col('language_description')
        .str.extract(r'\bPython \(([0-9,]+) bytes\)', 1)
        .str.replace_all(',', '').cast(pl.UInt64).alias('python_bytes'),
    )
    # Unknown main languages are not classified as non-Python. If Python
    # shares the largest byte count, conservatively exclude the repository.
    .filter(
        pl.col('largest_language_bytes').is_not_null()
        & (pl.col('python_bytes').is_null()
           | (pl.col('python_bytes') < pl.col('largest_language_bytes')))
    )
    .sort(['commit_count', 'repo_name'], descending=[True, False])
    .unique(subset=['repo_name'], maintain_order=True)
    .head(5)
    .collect()
)
assert repos.height == 5, 'Fewer than five repositories with known non-Python main languages'
repos.write_json(OUT / 'ranking.json')
answer = ', '.join(repos['repo_name'].to_list())
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(answer)
