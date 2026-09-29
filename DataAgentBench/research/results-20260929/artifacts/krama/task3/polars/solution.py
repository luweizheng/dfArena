import re, html, json
from pathlib import Path
import polars as pl
OUT=Path('/workspace/work')
def clean(s):
 return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>','',s))).strip()
def key(s):
 s=re.split(r' Metropolitan Statistical Area| Micropolitan Statistical Area| MSA',s)[0]
 return re.sub(r'[-–—]+','-',s).strip().lower()
a=pl.read_parquet('/workspace/data/domain_assets/files.parquet')
s=a.filter(pl.col('file_description').str.contains('metropolitan_statistics'))['content'][0].decode()
t=next(t for t in re.findall(r'<table\b.*?</table>',s,re.S) if 'The 387 metropolitan' in clean(t))
rows=[]
for tr in re.findall(r'<tr\b.*?</tr>',t,re.S):
 cells=[clean(c) for c in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.S)]
 if len(cells)>=3 and ' MSA' in cells[0]:
  rows.append((cells[0],key(cells[0]),int(cells[1].replace(',','')),int(cells[2].replace(',',''))))
p=pl.DataFrame(rows,schema=['msa','key','pop2024','pop2020'],orient='row').with_columns((pl.col('pop2020')+0.75*(pl.col('pop2024')-pl.col('pop2020'))).alias('pop2023')).filter(pl.col('pop2023')>1_000_000)
p.write_csv(OUT/'population.csv')
d=pl.read_parquet('/workspace/data/domain_docs/files.parquet')
records=[]
for doc in d['content']:
 if 'Metropolitan Area\tReport Summary' not in doc: continue
 for line in doc.splitlines():
  if '\t' not in line: continue
  name,summary=line.split('\t',1)
  if '2024' in summary and key(name) in p['key'].to_list(): records.append((key(name),summary))
r=pl.DataFrame(records,schema=['key','summary'],orient='row')
r.write_csv(OUT/'selected_records.csv')
print('population',p.height,'records',r.height,'unique',r['key'].n_unique())

# Counts may be comma-separated, space-grouped, or plain integers.
N=r'(\d+(?:[, ]\d{3})*)'
def theft_count(s):
 direct=re.search(N+r' identity theft (?:reports|complaints|cases)',s)
 if direct: return int(re.sub(r'\D','',direct[1]))
 rate=re.search(r'identity theft rate of .*?\('+N+r' total reports\)',s)
 if rate: return int(re.sub(r'\D','',rate[1]))
 patterns=[
  r'(?:were|totaled|reached|stood at|totaling|showed|from|with|to|of) '+N+r' and '+N+r' (?:reports|complaints|filed complaints|total reports|total filings)',
  r'^'+N+r' and '+N+r' complaints',
  r'(?:counts|totals) of '+N+r' and '+N,
  r'complaint counts .*? were '+N+r' and '+N,
  r'(?:reached|totaled) '+N+r' and '+N,
 ]
 for pat in patterns:
  m=re.search(pat,s)
  if m: return int(re.sub(r'\D','',m[2]))
 raise ValueError(s)
r=r.with_columns(pl.col('summary').map_elements(theft_count,return_dtype=pl.Int64).alias('thefts2024'))
assert r['key'].n_unique()==r.height
matched=p.join(r,on='key',how='inner',validate='1:1')
matched.write_csv(OUT/'matched_msas.csv')
average=matched.select(pl.col('thefts2024').mean()).item()
(OUT/'answer.json').write_text(json.dumps({'answer':f'{average:.4f}'}))
print('MSAs:',matched.height,'Total:',matched['thefts2024'].sum(),'Average:',f'{average:.4f}')
