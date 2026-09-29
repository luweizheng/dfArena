import pandas as pd, re, datetime, json, struct
from pathlib import Path
from shapely import from_wkb
from shapely.ops import unary_union, transform
from pyproj import Transformer
ROOT=Path('/workspace/data'); OUT=Path('/workspace/work')
docs=pd.read_parquet(ROOT/'domain_docs/files.parquet')
areas=['Western Great Basin','Northern California','Southern California','Northern Rockies','Rocky Mountains','Southern Area','Eastern Area','Great Basin','Northwest','Southwest','Alaska','Total']
area_re=re.compile('|'.join(areas))
date_re=re.compile(r'\b(?:\d{4}[-/]\d{4}|\d{8}|\d{4}/\d{4}|\d{2}[A-Za-z]{3}-\d{4}|[A-Za-z]+\d{2},\d{4})\b')
def dateparse(s):
 for f in ['%Y%m%d','%Y-%m%d','%Y/%m%d','%m%d/%Y','%d%m/%Y','%d%b-%Y','%b%d,%Y','%B%d,%Y']:
  try:return datetime.datetime.strptime(s,f)
  except ValueError:pass
rows=[]
for doc in docs.content:
 if 'Area\tReport' not in doc:continue
 for line in doc.splitlines():
  d=date_re.search(line);a=area_re.search(line)
  if not d or not a:continue
  dt=dateparse(d.group())
  if dt and 2014<=dt.year<=2024: rows.append((a.group(),dt,line))
r=pd.DataFrame(rows,columns=['area','date','line']).drop_duplicates()
r['year']=r.date.dt.year
latest=r[r.date.eq(r.groupby(['area','year']).date.transform('max'))].copy()
latest.to_csv(OUT/'latest_reports.csv',index=False)
print(latest.groupby(['area','year']).size().to_string())
print(latest.head(25).to_string(index=False))
# Numeric MMDD/YYYY and DDMM/YYYY forms are ambiguous: determine final
# report dates from explicit year-first or named-month representations.
def unambiguous(line):
 s=date_re.search(line).group()
 return not re.fullmatch(r'\d{4}/\d{4}',s) or s.startswith(('20','19'))
anchor=r[r.line.map(unambiguous)].groupby('year').date.max()
def finalmatch(row):
 s=date_re.search(row.line).group(); target=anchor[row.year]
 if row.date==target:return True
 if re.fullmatch(r'\d{4}/\d{4}',s):
  for fmt in ['%m%d/%Y','%d%m/%Y']:
   try:
    if datetime.datetime.strptime(s,fmt)==target:return True
   except ValueError:pass
 return False
latest=r[r.apply(finalmatch,axis=1)].copy()
print('Final dates',anchor.to_dict())
latest.to_csv(OUT/'latest_reports.csv',index=False)
light=r'(?:lightning-caused wildfires|lightning-caused fire occurrences|lightning-ignited fire events|lightning-source wildfire incidents|fires from lightning causes)'
metric=re.compile(r'(?:'+light+r'|acres burned by lightning-caused wildfires|lightning-caused acres burned|lightning-ignited burn acreage|lightning-source acres consumed|acreage from lightning-caused fires|human-caused wildfires|human-caused fire occurrences|human-ignited fire events|human-source wildfire incidents|fires from human causes|acres burned by human-caused wildfires|human-caused acres burned|human-ignited burn acreage|human-source acres consumed|acreage from human-caused fires)',re.I)
num=r'(?:N/A|\d[\d, ]*\d|\d)'
def extract(line):
 line=date_re.sub('',line)
 matches=list(metric.finditer(line))
 for i,m in enumerate(matches):
  if not re.fullmatch(light,m.group(),re.I):continue
  if 'respectively' in line:
   vals=re.findall(num,re.split(r'\b(?:were|totaled)\b',line)[-1])
   if len(vals)==len(matches):return vals[i]
  after=line[m.end():matches[i+1].start() if i+1<len(matches) else len(line)]
  before=line[matches[i-1].end() if i else 0:m.start()]
  a=re.match(r'\s*(?:=|at|\(|reached|totaled|in .*? stood at)?\s*('+num+r')',after)
  b=re.search('('+num+r')\s*$',before)
  if a:return a.group(1)
  if b:return b.group(1)
 return None
latest['value']=latest.line.map(extract)
lightrows=latest[latest.line.str.contains(light,case=False,regex=True)]
print('UNPARSED',lightrows[lightrows.value.isna()].line.to_list())
latest['fires']=latest.value.map(lambda v: float('nan') if v in (None,'N/A') else int(re.sub(r'[, ]','',v)))
annual=latest.groupby(['area','year']).fires.max().unstack()
print(annual.to_string());annual.to_csv(OUT/'annual_counts.csv')
totals=annual.sum(axis=1,min_count=1)

def geometry(b):
 flags=b[3]; env=(flags>>1)&7; offset=8+{0:0,1:32,2:48,3:48,4:64}[env]
 srid=struct.unpack('<i' if flags&1 else '>i',b[4:8])[0]
 g=from_wkb(b[offset:])
 if srid!=4326:g=transform(Transformer.from_crs(srid,4326,always_xy=True).transform,g)
 return g if g.is_valid else g.buffer(0)
gacc=pd.read_parquet(ROOT/'geo/gacc_2025.parquet')
gacc['geometry']=gacc.SHAPE.map(geometry)
mapping={'USAKACC':'Alaska','USCAONCC':'Northern California','USCAOSCC':'Southern California','USCORMC':'Rocky Mountains','USGASAC':'Southern Area','USMTNRC':'Northern Rockies','USNMSWC':'Southwest','USORNWC':'Northwest','USUTGBC':'Great Basin','USWIEACC':'Eastern Area'}
centers={mapping[k]:unary_union(list(g.geometry)) for k,g in gacc.groupby('GACCUnitID')}
counties=pd.read_parquet(ROOT/'geo/usa_adm2.parquet')
def state(s):
 if s.startswith('A county in '):return s.split('A county in ')[1].split(':')[0]
 if ' / ' in s:return s.split(' / ')[1]
 if ' is a county in ' in s:return s.split(' is a county in ')[1].split(', located')[0]
 return s.split(', ')[-2]
# Resolve state names from unambiguous descriptions, then propagate by state ID.
known=counties[counties.adm_description.str.contains(' / | is a county in |^A county in ',regex=True)].copy()
known['state']=known.adm_description.map(state)
name_by_id=known.groupby('adm1_id').state.agg(lambda x:x.mode().iloc[0])
for sid, group in counties[~counties.adm1_id.isin(name_by_id.index)].groupby('adm1_id'):
 names=[]
 for desc in group.adm_description:
  clean=desc.removesuffix(', United States')
  names.append(re.split(r', | — ',clean)[-1])
 name_by_id.loc[sid]=pd.Series(names).mode().iloc[0]
counties['state']=counties.adm1_id.map(name_by_id)
assert counties.state.notna().all()
counties['geometry']=counties.geom.map(geometry)
links=[]
for st,group in counties.groupby('state'):
 geom=unary_union(list(group.geometry))
 for area,boundary in centers.items():
  if geom.intersects(boundary):links.append((st,area))
links=pd.DataFrame(links,columns=['state','area']).drop_duplicates()
links['fires']=links.area.map(totals)
links.to_csv(OUT/'state_gacc_totals.csv',index=False)
scores=links.groupby('state').fires.sum().sort_values(ascending=False)
print(scores.head(15).to_string())
(OUT/'answer.json').write_text(json.dumps({'answer':scores.index[0]}))
