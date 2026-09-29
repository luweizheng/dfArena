from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work/answer.json')

def main():
    # Any declared Shell usage qualifies, regardless of the primary language.
    shell_repos = (
        pl.scan_parquet(DATA / 'metadata/languages.parquet')
        .filter(pl.col('language_description').str.contains(r'\bShell\b'))
        .select('repo_name')
    )
    apache_repos = (
        pl.scan_parquet(DATA / 'metadata/licenses.parquet')
        .filter(pl.col('license').str.to_lowercase() == 'apache-2.0')
        .select('repo_name')
    )
    # Semi-joins express repository membership without multiplying commit rows.
    eligible = shell_repos.join(apache_repos, on='repo_name', how='semi')
    message = pl.col('message')
    count = (
        pl.scan_parquet(DATA / 'artifacts/commits.parquet')
        .join(eligible, on='repo_name', how='semi')
        .filter(
            message.is_not_null()
            & (message.str.len_chars() < 1000)
            & ~message.str.contains(r'(?i)^(merge|update|test)')
        )
        .select(pl.len().alias('count'))
        .collect(engine='streaming')
        .item()
    )
    result = {'answer': f'{count:,} commit messages'}
    OUT.write_text(json.dumps(result) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
