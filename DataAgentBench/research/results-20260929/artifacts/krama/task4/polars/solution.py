import json,re
from pathlib import Path
from html.parser import HTMLParser
import polars as pl
OUT=Path('/workspace/work')
docs=pl.read_parquet('/workspace/data/domain_docs/files.parquet')
rows=[]; missing=[]
for content in docs.filter(pl.col('content').str.contains('Metropolitan Area\tReport Summary'))['content']:
 for line in content.splitlines():
  if '\t' not in line or '2024' not in line: continue
  name,s=line.split('\t',1)
  if 'Metropolitan Statistical Area' not in name: continue
  s=re.sub(r'(?<=\d)[, ](?=\d{3}(?:\D|$))','',s)
  patterns=[(r'identity theft rate of (\d+) per',1),(r'(\d+) and (\d+) per-100K rates',2),(r'(\d+) identity thefts and',1),
   (r'identity theft (?:reports|cases|complaints) \((\d+)(?: per |/)100',1),
   (r'identity theft complaints at (\d+) per',1),
   (r'rate/count pairs were \d+/\d+ and (\d+)/',1),
   (r'at rates of (\d+) and (\d+) per 100.*respectively',2),
   (r'(\d+) and (\d+) per 100',2),
   (r'(?:rates.*?(?:were|of)|rates.*?stood at) (\d+) and (\d+)',2)]
  rate=None
  # Identity theft is first in this specific wording.
  m=re.search(r'filed \d+ identity theft reports and .*?at rates of (\d+) and (\d+)',s)
  if m: rate=int(m[1])
  else:
   for pat,group in patterns:
    m=re.search(pat,s,re.I)
    if m: rate=int(m[group]);break
  if rate is None: missing.append(line)
  else: rows.append({'msa':name,'rate':rate,'source':line})
print('parsed',len(rows),'missing',len(missing))
for s in missing: print(s)
rates=pl.DataFrame(rows).sort('rate',descending=True)
print(rates.head(5))
assert not missing
rates.write_csv(OUT/'rates.csv')
class Tables(HTMLParser):
 def __init__(self): super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr': self.row=[]
  if tag in ('td','th'):self.cell=''
 def handle_data(self,data):
  if self.cell is not None:self.cell+=data
 def handle_endtag(self,tag):
  if tag in ('td','th') and self.cell is not None:
   if self.row is not None:self.row.append(self.cell.strip())
   self.cell=None
  if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
assets=pl.read_parquet('/workspace/data/domain_assets/files.parquet')
html=assets.filter(pl.col('file_description').str.contains('metropolitan_statistics'))['content'].item()
p=Tables();p.feed(html.decode())
print('HTML sample',p.rows[:15])
(OUT/'population_rows.json').write_text(json.dumps(p.rows))
def key(name):
 name=re.sub(r'\s+(?:Metropolitan Statistical Area|MSA).*$', '',name)
 return re.sub(r'[-–—]+','-',name).strip().lower()
poprows=[{'key':key(r[0]),'population_2024':int(r[1].replace(',','')),'population_2020':int(r[2].replace(',',''))} for r in p.rows if len(r)>=3 and re.fullmatch(r'[\d,]+',r[1]) and re.fullmatch(r'[\d,]+',r[2])]
pop=pl.DataFrame(poprows)
winner=rates.head(1).with_columns(pl.col('msa').map_elements(key,return_dtype=pl.String).alias('key'))
result=winner.join(pop,on='key',how='inner').with_columns((pl.col('population_2024')-pl.col('population_2020')).abs().alias('change'))
assert result.height==1,result
r=result.row(0,named=True)
print(r)
answer=f"{r['change']:,} people ({r['msa']}; {r['population_2020']:,} in 2020 to {r['population_2024']:,} in 2024)."
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
(OUT/'evidence.json').write_text(json.dumps(r,indent=2)+'\n')
