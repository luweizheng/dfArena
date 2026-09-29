import io,json,re
from datetime import datetime
from pathlib import Path
import pandas as pd
OUT=Path('/workspace/work')
docs=pd.read_parquet('/workspace/data/domain_docs/files.parquet')
gacc=pd.read_parquet('/workspace/data/geo/gacc_2025.parquet')
tables=[]
for s in docs.content:
    if 'Area\tReport\n' in s and 'Metropolitan' not in s[:s.index('Area\tReport')]:
        tables.append(pd.read_csv(io.StringIO(s[s.index('Area\tReport'):]),sep='\t'))
t=pd.concat(tables,ignore_index=True).dropna(subset=['Report'])
regions=sorted(t.Area.unique())
mapping={}
for region in regions:
    name='Rocky Mountain' if region=='Rocky Mountains' else region
    matches=gacc[gacc.GACCDescription.str.contains(name,regex=False)]
    if not matches.empty:
        mapping[region]=re.search(r'\b[A-Z]{2,5}CC\b',matches.iloc[0].GACCDescription).group()
# Dates are embedded in the report prose. Numeric four-digit suffixes use MMDD;
# leading four digits permit DDMM when the first pair cannot be a month.
datepat=re.compile(r'\b(?:20\d{2}[-/]\d{4}|\d{4}/20\d{2}|20\d{6}|\d{2}[A-Za-z]{3}-20\d{2}|[A-Za-z]+\d{2},20\d{2})\b')
def parse_date(s):
    if re.fullmatch(r'20\d{2}[-/]\d{4}',s) and int(s[5:7])<=12: return datetime.strptime(s[:4]+s[5:],'%Y%m%d')
    if re.fullmatch(r'\d{4}/20\d{2}',s):
        return datetime.strptime(s,'%d%m/%Y' if int(s[2:4])<=12 else '%m%d/%Y')
    for fmt in ['%Y%m%d','%d%b-%Y','%b%d,%Y','%B%d,%Y']:
        try:return datetime.strptime(s,fmt)
        except ValueError:pass
    raise ValueError(s)
# Resolve ambiguous MMDD/DDMM tokens by support from explicitly formatted dates
# across the source reports, whose reporting dates recur across regions/metrics.
from collections import Counter
support=Counter()
for report in t.Report:
    for token in datepat.findall(report):
        if not re.fullmatch(r'\d{4}/20\d{2}',token):
            try:support[parse_date(token)]+=1
            except ValueError:pass
base_parse=parse_date
def parse_date(s):
    if re.fullmatch(r'\d{4}/20\d{2}',s):
        candidates=[]
        for fmt in ['%m%d/%Y','%d%m/%Y']:
            try:candidates.append(datetime.strptime(s,fmt))
            except ValueError:pass
        if candidates:return max(candidates,key=lambda d:support[d])
    return base_parse(s)
records=[]
for row in t.itertuples():
    if row.Area not in mapping:continue
    for line in row.Report.splitlines():
        m=datepat.search(line)
        if not m:continue
        date=parse_date(m.group())
        if 2020<=date.year<=2023:
            records.append((row.Area,date,date.year,line))
r=pd.DataFrame(records,columns=['region','date','year','line']).drop_duplicates()
r.to_csv(OUT/'reports.csv',index=False)
latest=r[r.date.eq(r.groupby(['region','year']).date.transform('max'))]
latest.to_csv(OUT/'latest_reports.csv',index=False)

metric=re.compile(r'(?:human-caused acres burned|human-ignited burn acreage|human-source acres consumed|acreage from human-caused fires|acres burned by human-caused wildfires)',re.I)
number=r'(?:\d[\d, ]*\d|\d|N/A)'
def acres(line):
    m=metric.search(line)
    if not m:return None
    # Two metrics followed by two numbers in matching order.
    if 'respectively' in line:
        pivot=re.search(r' (?:were|totaled|stood at|reached) ',line)
        names=line[:pivot.start()]
        names_parts=re.split(r', and | and |, ',names)
        pos=next(i for i,n in enumerate(names_parts) if metric.search(n))
        values=line[pivot.end():].split(', respectively')[0]
        vals=re.split(r', and | and |, ',values)
        v=vals[pos].strip()
        return None if v=='N/A' else float(re.sub('[, ]','',v))
    tail=line[m.end():]
    aft=re.match(r'\s*(?:=|at|\(|reached|totaled|stood at)\s*('+number+r')',tail,re.I)
    if not aft:
        aft=re.match(r'\s+in .+? (?:stood at|were)\s+('+number+r')',tail,re.I)
    if aft:v=aft.group(1)
    else:
        bef=re.search('('+number+r')\s*$',line[:m.start()])
        if not bef:raise ValueError(line)
        v=bef.group(1)
    return None if v=='N/A' else float(re.sub('[, ]','',v))
r['acres']=r.line.map(acres)
a=r.dropna(subset=['acres']).copy()
a=a[a.date.eq(a.groupby(['region','year']).date.transform('max'))]
a.to_csv(OUT/'latest_human_acres.csv',index=False)
print(a[['region','year','date','acres']].sort_values(['region','year']).to_string(index=False))
assert a.groupby(['region','year']).acres.nunique().max()==1
annual=a.drop_duplicates(['region','year'])
assert len(annual)==len(mapping)*4
totals=annual.groupby('region').acres.sum().sort_values(ascending=False)
print(totals)
(OUT/'answer.json').write_text(json.dumps({'answer':mapping[totals.idxmax()]}))
