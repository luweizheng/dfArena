import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
commits = pd.read_parquet(DATA / 'artifacts/commits.parquet', columns=['repo_name', 'commit'])
counts = commits.groupby('repo_name')['commit'].count().rename('commit_count').reset_index()
languages = pd.read_parquet(DATA / 'metadata/languages.parquet')
languages = languages[languages['repo_name'].isin(counts['repo_name'])].copy()

# Strip prose around language/byte pairs, then compare their byte counts.
prose = re.compile(r'^(?:The codebase includes: |This repository is mainly written in |The majority of the code is in |While most of the project is built in |with additional code in |followed by |it also incorporates )')
def main_language(description):
    if pd.isna(description):
        return None
    pairs = re.findall(r'([^(),]+?)\s*\(([\d,]+) bytes\)', description)
    parsed = [(prose.sub('', name.strip()), int(size.replace(',', ''))) for name, size in pairs]
    if not parsed:
        raise ValueError(f'Unrecognized language description: {description}')
    return max(parsed, key=lambda item: item[1])[0]

languages['main_language'] = languages['language_description'].map(main_language)
ranked = counts.merge(languages[['repo_name', 'main_language']], on='repo_name', how='inner', validate='one_to_one')
ranked = ranked[ranked['main_language'].notna() & ranked['main_language'].ne('Python')]
ranked = ranked.sort_values(['commit_count', 'repo_name'], ascending=[False, True]).head(5)
assert len(ranked) == 5
ranked.to_csv(OUT / 'ranking.csv', index=False)
answer = {'answer': ', '.join(ranked['repo_name'])}
(OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
print(ranked.to_string(index=False))
print(json.dumps(answer))

if __name__ == '__main__':
    pass
