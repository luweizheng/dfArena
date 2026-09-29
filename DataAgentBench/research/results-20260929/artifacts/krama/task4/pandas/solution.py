import pandas as pd
import re,json
from html.parser import HTMLParser
from pathlib import Path
OUT=Path('/workspace/work')
docs=pd.read_parquet('/workspace/data/domain_docs/files.parquet')
N=r'(\d+(?:[, ]\d{3})*)'
def num(v):return int(re.sub(r'[, ]','',v))
def rate(s):
    for pattern in [r'identity theft rate of '+N+r' per 100',r'identity theft complaints at '+N+r' per 100',N+r' identity thefts and']:
        m=re.search(pattern,s)
        if m:return num(m[1])
    m=re.search(N+' and '+N+r' per-100K rates',s)
    if m:return num(m[2])
    m=re.search(r'identity theft (?:reports|cases) \('+N+r'(?: per |/)100',s)
    if m:return num(m[1])
    m=re.search(r'identity theft rate/count pairs were '+N+'/'+N+' and '+N+'/'+N,s)
    if m:return num(m[3])
    m=re.search(N+' and '+N+r' per 100(?:K|,000)',s)
    if m:
        return num(m[1] if 'at rates' in s and 'identity theft reports and' in s else m[2])
    m=re.search(r'per-100K rates of '+N+' and '+N,s)
    if m:return num(m[2])
    m=re.search(r'(?:[Pp]er-100K rates|rates per 100K).*?were '+N+' and '+N,s)
    if m:return num(m[2])
    return None
records=[]
for content in docs.content:
    if 'Metropolitan Area\tReport Summary' not in content:continue
    for line in content.splitlines():
        if '\t' not in line or '2024' not in line:continue
        name,s=line.split('\t',1)
        records.append(dict(msa=name,rate=rate(s),summary=s))
r=pd.DataFrame(records)
print('unparsed',r.rate.isna().sum())
for s in r.loc[r.rate.isna(),'summary']:print(s)
print(r.sort_values('rate',ascending=False).head(8).to_string(index=False))
r.to_csv(OUT/'extracted_rates.csv',index=False)
assets=pd.read_parquet('/workspace/data/domain_assets/files.parquet')
html=assets.loc[assets.file_description.str.contains('metropolitan_statistics',case=False),'content'].iloc[0].decode()
class Tables(HTMLParser):
    def __init__(self):super().__init__();self.tables=[];self.depth=0;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='table':
            if self.depth==0:self.rows=[]
            self.depth+=1
        if self.depth==1:
            if tag=='tr':self.row=[]
            if tag in ('td','th'):self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if self.depth==1:
            if tag in ('td','th') and self.cell is not None:self.row.append(''.join(self.cell).strip());self.cell=None
            if tag=='tr':self.rows.append(self.row)
        if tag=='table':
            self.depth-=1
            if self.depth==0:self.tables.append(self.rows)
p=Tables();p.feed(html)
for i,t in enumerate(p.tables):
    print('TABLE',i,'rows',len(t),t[:2])
    pd.DataFrame(t).to_csv(OUT/f'population_table_{i}.csv',index=False)

assert r.rate.notna().all(), 'Unparsed report rates'
metros=r[r.msa.str.contains('Metropolitan Statistical Area',regex=False)]
winner=metros.loc[metros.rate.idxmax()]
def canonical(name):
    name=re.sub(r'\s+(?:Metropolitan Statistical Area|MSA).*$', '',name,flags=re.I)
    name=re.sub(r'[—–−]|--','-',name)
    return re.sub(r'\s+',' ',name).strip().casefold()
pop_tables=[pd.DataFrame(t[1:],columns=t[0]) for t in p.tables if t and '2024estimate' in t[0] and '2020census' in t[0]]
pop=pd.concat(pop_tables,ignore_index=True)
matched=pop[pop['Metropolitan statistical area'].map(canonical)==canonical(winner.msa)]
assert len(matched)==1
row=matched.iloc[0]
p2020=num(row['2020census']);p2024=num(row['2024estimate'])
change=abs(p2024-p2020)
answer=f"{change:,} people."
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
(OUT/'calculation.json').write_text(json.dumps({'msa':winner.msa,'rate_per_100K':int(winner.rate),'population_2020':p2020,'population_2024':p2024,'absolute_change':change},indent=2)+'\n')
print(answer)
