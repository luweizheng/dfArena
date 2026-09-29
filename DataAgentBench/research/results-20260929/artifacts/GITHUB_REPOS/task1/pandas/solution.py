import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

languages = pd.read_parquet(DATA / 'metadata/languages.parquet', columns=['repo_name', 'language_description'])
files = pd.read_parquet(DATA / 'artifacts/files.parquet', columns=['repo_name', 'path', 'id'])
contents = pd.read_parquet(DATA / 'artifacts/contents.parquet', columns=['id', 'content'])

# Exclude repositories using Python in any declared language position.
python_repos = languages.loc[
    languages.language_description.str.contains(r'\bPython\b', case=False, na=False), 'repo_name'
]
non_python_repos = languages.loc[
    languages.language_description.notna() & ~languages.repo_name.isin(python_repos), ['repo_name']
]
# README.md may occur at the root or in a nested directory.
readmes = files.loc[files.path.str.rsplit('/', n=1).str[-1].eq('README.md')]
readmes = readmes.merge(non_python_repos, on='repo_name', how='inner', validate='many_to_one')
# An inner join excludes file records whose blobs are unavailable.
available = readmes.merge(contents, on='id', how='inner', validate='many_to_one')
available = available.loc[available.content.notna()].copy()
available['has_copyright'] = available.content.str.contains(r'copyright|©|&copy;', case=False, na=False)
numerator = int(available.has_copyright.sum())
denominator = len(available)
if not denominator:
    raise ValueError('No eligible README.md files with available contents')
proportion = numerator / denominator
answer = f'{proportion:.2%} ({numerator} of {denominator} README.md files with available contents).'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
available[['repo_name', 'path', 'id', 'has_copyright']].to_csv(OUT / 'eligible_readmes.csv', index=False)
print(answer)

if __name__ == '__main__':
    pass
