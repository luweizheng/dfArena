import io,json,re
from pathlib import Path
import pandas as pd
DATA=Path('/workspace/data')
OUT=Path('/workspace/work')
header='Community Code\tCounty Code\tLocation\tResult'
docs=pd.read_parquet(DATA/'domain_docs/files.parquet')
b=pd.concat([pd.read_csv(io.StringIO(s[s.index(header):]),sep='\t',dtype=str) for s in docs.content if header in s],ignore_index=True)
b=b.dropna(subset=['Location','Result']).reset_index(drop=True)
patterns=[r'^Water sample from (.*?) — a (?:Fresh|Marine) beach.*?collected on (.*?)\.$',r'^On (.*?), a water sample was taken at (.*?) \((?:Fresh|Marine) beach\)',r'^Location: (.*?), .*?Sample date: (.*?)\.$',r'^(.*?) is a (?:Fresh|Marine) beach.*?Sample collected on (.*?)\.$',r'^Sample collected at (.*?) \((?:Fresh|Marine)\).*? on (.*?)\.$',r'^(.*?) \((?:Fresh|Marine) beach, .*?was sampled on (.*?)\.$',r'^.*?: (.*?) \((?:Fresh|Marine) beach\), sampled on (.*?)\.$',r'^(.*?): water sample at (.*?) \((?:Fresh|Marine)\)']
def extract(s):
 for i,p in enumerate(patterns):
  m=re.search(p,s)
  if m:
   a,c=m.groups()
   return (c,a) if i in (1,7) else (a,c)
 raise ValueError(s)
def year(s):
 s=s.strip()
 if re.match(r'^\d{12}$',s):return 2000+int(s[:2])
 if re.match(r'^\d{2}-\d{2}-\d{2} ',s):return 2000+int(s[:2])
 m=re.search(r'(?:19|20)\d{2}',s)
 if m:return int(m.group())
 raise ValueError(s)
def canonical(s):return re.sub('[^a-z0-9]','',s.lower())
def code(s):return int(re.search(r'\d+',s).group())
b[['beach','date']]=pd.DataFrame(b.Location.map(extract).tolist(),index=b.index)
b['year']=b.date.map(year)
b['failed']=b.Result.str.contains(r'exceeded|failed to meet|constitutes a violation|non-compliant|exceeding|did not meet|surpassed|; violation recorded',regex=True)
b['community']=b['Community Code'].map(code);b['county']=b['County Code'].map(code);b['key']=b.beach.map(canonical)
counts=b[b.year.between(2012,2018)&b.failed].groupby(['community','county','key']).size().sort_values(ascending=False)
print(counts.head(10).to_string())
assert len(counts[counts==counts.iloc[0]])==1
winner=counts.index[0]
t=pd.read_parquet(DATA/'geo/beach_water_temperature.parquet')
t['community']=t.community_code.map(code);t['county']=t.county_code.map(code);t['key']=t.beach_name.map(canonical)
t['year']=t.sample_date.map(year)
s=t[(t.community==winner[0])&(t.county==winner[1])&(t.key==winner[2])&t.year.between(2012,2018)].copy()
def celsius(v):
 if pd.isna(v) or not v.strip():return float('nan')
 n=float(re.search(r'[-+]?\d+(?:\.\d+)?',v).group())
 u=v.lower()
 if 'f' in u:return (n-32)*5/9
 if 'k' in u:return n-273.15
 if 'c' in u:return n
 raise ValueError(v)
s['celsius']=s.water_temp.map(celsius)
assert s.celsius.notna().any()
print(s[['beach_name','sample_date','water_temp','celsius']].to_string(index=False))
avg=s.celsius.mean()
s.to_csv(OUT/'selected_temperatures.csv',index=False)
(OUT/'answer.json').write_text(json.dumps({'answer':f'{avg:.2f} °C'},ensure_ascii=False)+'\n')
print('Average:',avg,'Readings:',s.celsius.count())
if __name__=='__main__':pass
