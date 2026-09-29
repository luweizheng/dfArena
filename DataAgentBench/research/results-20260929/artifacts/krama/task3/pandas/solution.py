import pandas as pd
import re,json
from html.parser import HTMLParser
from pathlib import Path
OUT=Path('/workspace/work')
class Rows(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=[];self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row=[]
  if tag in ('td','th'):self.cell=''
 def handle_data(self,s):
  if self.cell is not None:self.cell+=s
 def handle_endtag(self,tag):
  if tag in ('td','th') and self.cell is not None:self.row.append(self.cell.strip());self.cell=None
  if tag=='tr':self.rows.append(self.row)
def key(s):
 s=re.split(r'\s+(?:MSA|Metropolitan Statistical Area)',s)[0]
 s=re.sub(r'[–—−]|--+','-',s)
 return re.sub(r'\s+',' ',s).strip().lower()
a=pd.read_parquet('/workspace/data/domain_assets/files.parquet')
h=Rows();h.feed(a.loc[a.file_description.str.contains('metropolitan_statistics',case=False),'content'].iloc[0].decode())
print(h.rows[12:15])
pop=[]
for row in h.rows:
 if len(row)>=4 and re.search(r', [A-Z]{2}(?:-[A-Z]{2})* MSA',row[0]):
  pop.append((row[0],int(row[1].replace(',','')),int(row[2].replace(',',''))))
p=pd.DataFrame(pop,columns=['msa','pop2024','pop2020']);p['key']=p.msa.map(key);p['pop2023']=p.pop2020+.75*(p.pop2024-p.pop2020)
p=p[p.pop2023>1000000]
d=pd.read_parquet('/workspace/data/domain_docs/files.parquet')
lines=[]
for s in d.content:
 for line in s.splitlines():
  if '\t' in line and 'Metropolitan Statistical Area' in line and '2024' in line:
   name,summary=line.split('\t',1)
   if key(name) in set(p.key):lines.append((name,summary))
p.to_csv(OUT/'population.csv',index=False)
pd.DataFrame(lines,columns=['msa','summary']).to_csv(OUT/'reports2024.csv',index=False)
print('pop',len(p),'reports',len(lines))
for name,s in lines:print(name,'\t',s)
# Match counts separately from the per-capita rates in each prose template.
num=r'(\d+(?:[, ]\d{3})*)'
patterns=[
 num+r' identity theft (?:reports|complaints|cases)',
 r'identity theft rate of '+num+r' per 100K \('+num+r' total reports\)',
 r'(?:corresponding to|from|with|totaling|totaled|reached|stood at|were|showed) '+num+r' and '+num+r'(?: total reports| total filings| filed complaints| reports| complaints|, at rates|, yielding|, corresponding)',
 r'(?:underlying report counts|absolute counts|report totals|report counts|counts) of '+num+r' and '+num,
 r'^'+num+r' and '+num+r' complaints were filed',
]
records=[]
for name,s in lines:
 matches=[]
 for pattern in patterns:
  m=re.search(pattern,s)
  if m:matches.append(int(re.sub(r'[, ]','',m.groups()[-1])))
 assert matches and len(set(matches))==1,(name,s,matches)
 records.append((key(name),matches[0],s))
t=pd.DataFrame(records,columns=['key','thefts2024','source_text'])
assert not t.key.duplicated().any()
joined=p.merge(t,on='key',how='inner',validate='one_to_one')
joined.to_csv(OUT/'matched_msas.csv',index=False)
answer=f'{joined.thefts2024.mean():.4f}'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print('Matched MSAs:',len(joined),'Total thefts:',joined.thefts2024.sum(),'Average:',answer)
