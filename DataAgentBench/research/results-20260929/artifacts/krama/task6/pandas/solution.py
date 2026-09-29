import json,re,io
from pathlib import Path
import pandas as pd
DATA=Path('/workspace/data')
OUT=Path('/workspace/work')
def canonical(s): return re.sub(r'[^a-z0-9]','',str(s).lower())
def code(s):
    m=re.search(r'\d+',str(s))
    return int(m[0]) if m else None
def celsius(s):
    value=float(re.search(r'[-+]?\d+(?:\.\d+)?',s)[0])
    unit=s.lower()
    if 'f' in unit: return (value-32)*5/9
    if 'k' in unit: return value-273.15
    assert 'c' in unit,s
    return value
x=pd.read_parquet(DATA/'geo/beach_water_temperature.parquet')
# Calendar years suffice for the inclusive whole-year interval, avoiding
# irrelevant month/day ambiguity in numeric dates.
x['year']=x.sample_date.str.extract(r'((?:19|20)\d{2})').astype(int)
x['temperature_c']=x.water_temp.map(celsius)
x['community']=x.community_code.map(code)
x['county']=x.county_code.map(code)
x['beach']=x.beach_name.map(canonical)
means=x.loc[x.year.between(2008,2016)].groupby(['community','county','beach']).temperature_c.agg(['mean','count']).sort_values('mean')
means.to_csv(OUT/'temperature_means.csv')
key=means.index[0]
assert means.iloc[0]['mean']<means.iloc[1]['mean']
name=x.loc[(x.community==key[0])&(x.county==key[1])&(x.beach==key[2]),'beach_name'].iloc[0].strip()
docs=pd.read_parquet(DATA/'domain_docs/files.parquet')
frames=[]
header='Community Code\tCounty Code\tLocation\tResult'
for s in docs.content:
    if header in s:
        frames.append(pd.read_csv(io.StringIO(s[s.index(header):]),sep='\t',dtype=str))
b=pd.concat(frames,ignore_index=True)
b=b.loc[(b['Community Code'].map(code)==key[0])&(b['County Code'].map(code)==key[1])].copy()
b=b.loc[b.Location.map(canonical).str.contains(key[2],regex=False)].copy()
def year_from_location(s):
    # Four-digit separated dates, textual dates, and compact YYYYMMDD dates.
    m=re.search(r'(?<!\d)((?:19|20)\d{2})(?=[-/ ]|\d{4}(?:T| |\d{6}))',s)
    if m:return int(m[1])
    # Compact YYMMDDhhmmss or YY-MM-DD hh-mm-ss.
    m=re.search(r'(?<!\d)(\d{2})(?:\d{10}|-\d{2}-\d{2}\s+\d{2}-\d{2}-\d{2})(?!\d)',s)
    if m:return 2000+int(m[1])
    raise ValueError(s)
b['year']=b.Location.map(year_from_location)
b=b.loc[b.year.between(2008,2016)].copy()
positive=r'failed|surpassed|constitutes a violation|exceed|in violation|violation was recorded|violated'
negative=r'passed|compliant|met water quality|meeting all|no violation|no quality violation|within.*(?:limit|acceptable)'
b['violation']=b.Result.str.contains(positive,case=False,regex=True)
known=b.violation|b.Result.str.contains(negative,case=False,regex=True)
assert known.all(),b.loc[~known,'Result'].tolist()
assert len(b)>0
b.to_csv(OUT/'selected_bacterial_samples.csv',index=False)
rate=100*b.violation.sum()/len(b)
answer=f'{name}: {rate:.2f}%.'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(means.head().to_string());print(b.groupby('year').violation.agg(['sum','count']).to_string());print(f'Violations: {b.violation.sum()}; samples: {len(b)}');print(answer)
