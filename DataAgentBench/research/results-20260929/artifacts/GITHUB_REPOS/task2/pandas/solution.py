import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

languages = pd.read_parquet(DATA / 'metadata/languages.parquet')
files = pd.read_parquet(DATA / 'artifacts/files.parquet')
contents = pd.read_parquet(
    DATA / 'artifacts/contents.parquet',
    columns=['id', 'repo_data_description'],
)

# Include repositories with any declared Swift code, regardless of primary language.
swift_repos = languages.loc[
    languages['language_description'].str.contains(r'\bSwift\b', na=False),
    'repo_name',
].drop_duplicates()

# A file ID must uniquely identify a row in the full files table.
unique_ids = files['id'].value_counts().loc[lambda counts: counts.eq(1)].index
eligible_files = files.loc[
    files['id'].isin(unique_ids)
    & files['repo_name'].isin(swift_repos)
    & files['path'].str.endswith('.swift', na=False)
]

metadata = contents.loc[
    contents['repo_data_description'].str.contains('non-binary', case=False, na=False)
].copy()
metadata['copies'] = pd.to_numeric(
    metadata['repo_data_description'].str.extract(r'(\d[\d,]*) times', expand=False)
    .str.replace(',', '', regex=False),
    errors='raise',
)
metadata = metadata[['id', 'copies']].drop_duplicates()
assert not metadata['id'].duplicated().any(), 'Conflicting copy counts for a blob'
candidates = eligible_files.merge(metadata, on='id', validate='one_to_one')
assert not candidates.empty, 'No qualifying Swift files'
assert candidates['copies'].notna().all(), 'Missing copy count'
winners = candidates.loc[candidates['copies'].eq(candidates['copies'].max())]
candidates.sort_values('copies', ascending=False).to_csv(OUT / 'candidates.csv', index=False)
answer = '; '.join(
    f"{row.repo_name}: {row.path} (ID: {row.id}), {int(row.copies)} copies"
    for row in winners.itertuples(index=False)
) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(answer)
