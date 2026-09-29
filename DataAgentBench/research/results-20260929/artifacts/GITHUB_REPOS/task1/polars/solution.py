import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    languages = pl.scan_parquet(DATA / 'metadata/languages.parquet')
    # A repository is eligible only if its language metadata is available
    # and none of its language records mentions Python.
    eligible = (languages.group_by('repo_name').agg(
        pl.col('language_description').is_not_null().any().alias('known'),
        pl.col('language_description').str.contains(r'(?i)\bpython\b').fill_null(False).any().alias('uses_python'),
    ).filter(pl.col('known') & ~pl.col('uses_python')).select('repo_name'))
    readmes = (pl.scan_parquet(DATA / 'artifacts/files.parquet')
        .filter(pl.col('path').str.contains(r'(^|/)README\.md$'))
        .join(eligible, on='repo_name', how='semi'))
    contents = (pl.scan_parquet(DATA / 'artifacts/contents.parquet')
        .select('id', 'content').filter(pl.col('content').is_not_null()))
    # File IDs connect each repository file to its available blob contents.
    available = (readmes.join(contents, on='id', how='inner')
        .with_columns(pl.col('content').str.contains(r'(?i)copyright').alias('has_copyright'))
        .collect())
    total = available.height
    count = available['has_copyright'].sum()
    if not total:
        raise ValueError('No eligible README.md files with available contents')
    available.select('repo_name', 'ref', 'path', 'id', 'has_copyright').write_csv(OUT / 'readme_audit.csv')
    answer = f'{count / total:.2%} ({count} of {total} README.md files with available contents).'
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(answer)

if __name__ == '__main__':
    main()
