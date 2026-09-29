import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    languages = pd.read_parquet(DATA / 'metadata/languages.parquet', columns=['repo_name', 'language_description'])
    licenses = pd.read_parquet(DATA / 'metadata/licenses.parquet', columns=['repo_name', 'license'])
    # Shell may be any listed language, rather than the primary language.
    shell = languages.loc[languages['language_description'].str.contains(r'\bShell\s*\(', regex=True, na=False), 'repo_name']
    apache = licenses.loc[licenses['license'].str.lower().eq('apache-2.0'), 'repo_name']
    eligible = pd.Index(shell).intersection(pd.Index(apache))
    commits = pd.read_parquet(DATA / 'artifacts/commits.parquet', columns=['repo_name', 'message'])
    messages = commits.loc[commits['repo_name'].isin(eligible), 'message']
    valid = (messages.notna() & messages.str.len().lt(1000)
             & ~messages.str.lower().str.startswith(('merge', 'update', 'test'), na=False))
    count = int(valid.sum())
    answer = {'answer': f'{count:,} commit messages.'}
    (OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps({'eligible_repositories': len(eligible), 'repository_commit_rows': len(messages), 'count': count}))

if __name__ == '__main__':
    main()
