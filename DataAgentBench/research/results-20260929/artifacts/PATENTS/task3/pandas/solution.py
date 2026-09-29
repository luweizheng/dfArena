import json
import re
from pathlib import Path
import pandas as pd

OUT = Path('/workspace/work')
p = pd.read_parquet('/workspace/data/publication/publicationinfo.parquet', columns=['Patents_info','citation','cpc'],use_threads=False)
s = p['Patents_info']
p['assignee'] = s.str.extract(r'^(.*?) holds the ', expand=False).fillna(s.str.extract(r'(?:owned by|assigned to|held by|belonging to) (.*?)(?: and has |, with )',expand=False))
p['publication'] = s.str.extract(r'(?:publication|pub\.) (?:number|no\.) ([A-Z0-9-]+)',expand=False)
assert p.assignee.notna().all(), s[p.assignee.isna()].head().tolist()
assert p.publication.notna().all(), s[p.publication.isna()].head().tolist()
targets = set(p.loc[p.assignee.eq('UNIV CALIFORNIA'),'publication'])
# Extract citation publication identifiers, then join to target publication IDs.
refs = p.citation.fillna('').str.findall(r'"publication_number"\s*:\s*"([^"]+)"').explode().dropna()
matched_indices = refs.index[refs.isin(targets)].unique()
citing = p.loc[matched_indices].copy()
citing = citing[citing.assignee.ne('UNIV CALIFORNIA')]
citing['subclass'] = citing.cpc.map(lambda raw: sorted({entry['code'][:4] for entry in json.loads(raw or '[]') if entry.get('first') is True}))
rows = citing[['assignee','publication','subclass']].explode('subclass').dropna(subset=['subclass'])
defs = pd.read_parquet('/workspace/data/CPCDefinition/cpc_definition.parquet',columns=['symbol','titleFull'],use_threads=False)
result = rows.merge(defs, left_on='subclass',right_on='symbol',how='left')
assert result.titleFull.notna().all(), result[result.titleFull.isna()].subclass.unique()
result[['assignee','publication','subclass','titleFull']].drop_duplicates().to_csv(OUT/'citation_details.csv',index=False)
pairs = result[['assignee','subclass','titleFull']].drop_duplicates().sort_values(['assignee','subclass','titleFull'])
pairs.to_csv(OUT/'assignee_subclasses.csv',index=False)
answer = '\n'.join(f'{r.assignee} — {r.subclass}: {r.titleFull}' for r in pairs.itertuples(index=False))
(OUT/'answer.json').write_text(json.dumps({'answer':answer},ensure_ascii=False,indent=2)+'\n')
print(f'Target publications: {len(targets)}; citing publications: {citing.publication.nunique()}; assignees with primary CPC subclasses: {pairs.assignee.nunique()}; distinct pairs: {len(pairs)}')
print(answer)
