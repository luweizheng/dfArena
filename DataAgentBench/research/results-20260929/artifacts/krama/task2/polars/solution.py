import polars as pl
import re,datetime,json,struct
from pathlib import Path
ROOT=Path('/workspace/data'); OUT=Path('/workspace/work')
pat=re.compile(r'\b(?:\d{4}[-/]\d{4}|\d{4}/\d{2,4}|\d{8}|[A-Za-z]+\d{2},\d{2,4}|\d{2}[A-Za-z]+-\d{2,4})\b')
def date(s):
 for fmt in ('%Y-%m%d','%Y/%m%d','%Y%m%d','%m%d/%Y','%d%m/%Y','%b%d,%Y','%B%d,%Y','%d%b-%Y','%m%d/%y','%d%m/%y','%b%d,%y','%B%d,%y','%d%b-%y','%y%m%d'):
  try:return datetime.datetime.strptime(s,fmt).date()
  except ValueError:pass
 return None
rows=[]
for c in pl.read_parquet(ROOT/'domain_docs/files.parquet')['content']:
 if 'Area\tReport' not in c or 'lightning' not in c.lower():continue
 area=None
 for line in c.split('Area\tReport',1)[1].splitlines():
  if '\t' in line:area,line=line.split('\t',1)
  m=pat.search(line)
  if m:
   d=date(m.group())
   if d and 2014<=d.year<=2024:rows.append((area,d,d.year,line))
reports=pl.DataFrame(rows,schema=['area','date','year','line'],orient='row').unique()
# Determine year-end dates from unambiguous date spellings across the reports.
def unambiguous(line):
 t=pat.search(line).group()
 if re.fullmatch(r'\d{4}/\d{4}',t) and not t.startswith(('19','20')):
  return int(t[:2])>12 or int(t[2:4])>12 or t[:2]==t[2:4]
 return True
ends=reports.filter(pl.col('line').map_elements(unambiguous,return_dtype=pl.Boolean)).group_by('year').agg(pl.col('date').max())
print('Report dates',ends.sort('year'))
def candidates(line):
 t=pat.search(line).group();ds=[date(t)]
 if re.fullmatch(r'\d{4}/\d{4}',t):
  for fmt in ('%m%d/%Y','%d%m/%Y'):
   try:ds.append(datetime.datetime.strptime(t,fmt).date())
   except ValueError:pass
 return ds
endmap=dict(ends.iter_rows())
latest=reports.filter(pl.struct('year','line').map_elements(lambda r:endmap[r['year']] in candidates(r['line']),return_dtype=pl.Boolean)).with_columns(pl.col('year').replace_strict(endmap,return_dtype=pl.Date).alias('date'))
metric=r'(?<!acres burned by )(?:lightning-caused wildfires|lightning-caused fire occurrences|lightning-ignited fire events|lightning-source wildfire incidents|fires from lightning causes)'
num=r'(?:N/A|\d[\d, ]*\d|\d)'
def count(line):
 s=pat.sub('',line,count=1).lower()
 # Paired measures with values supplied in the same order.
 if 'respectively' in s and re.search(metric,s):
  m=re.search(r'(.+?)\s+(?:were|was)\s+('+num+r')\s+and\s+('+num+r')',s,re.I)
  if m:
   labels=m.group(1).split(' and ')
   for i,label in enumerate(labels):
    if re.search(metric,label):return toint(m.group(i+2))
 # Number before the measure.
 m=re.search(r'('+num+r')\s+'+metric,s,re.I)
 if m:return toint(m.group(1))
 # Measure before its value; limit to the connecting phrase.
 m=re.search(metric+r'(?:\s+(?:in [a-z ]+? stood at|totaled|reached|at)|\s*[=(])\s*('+num+r')',s,re.I)
 if m:return toint(m.group(1))
 return None
def toint(x):return None if x.upper()=='N/A' else int(re.sub(r'[, ]','',x))
latest=latest.with_columns(pl.col('line').map_elements(count,return_dtype=pl.Int64).alias('fires'))
latest.write_csv(OUT/'latest.csv')
annual=latest.filter(pl.col('fires').is_not_null()).with_columns(pl.col('line').map_elements(unambiguous,return_dtype=pl.Boolean).alias('unambiguous')).filter(pl.col('unambiguous')==pl.col('unambiguous').max().over(['area','year'])).select('area','year','date','fires').unique()
print('annual counts',annual.group_by('area').len().sort('area'))
for a in latest['area'].unique():
 for y in range(2014,2025):
  if annual.filter((pl.col('area')==a)&(pl.col('year')==y)).height==0 and a!='Western Great Basin':
   print('MISSING',a,y,latest.filter((pl.col('area')==a)&(pl.col('year')==y))['line'].to_list())
annual.write_csv(OUT/'annual.csv')
# Disambiguate numeric dates by reconciling the annual regional figures
# against the national count supplied in the same report.
import itertools
chosen=[]
for y in range(2014,2025):
 yr=annual.filter(pl.col('year')==y)
 areas=sorted(a for a in yr['area'].unique() if a!='Total')
 opts=[yr.filter(pl.col('area')==a)['fires'].unique().to_list() for a in areas]
 totals=yr.filter(pl.col('area')=='Total')['fires'].to_list()
 matches=[v for v in itertools.product(*opts) if sum(v) in totals]
 print(y,'national totals',totals,'matching combinations',len(matches))
 if not matches and all(len(v)==1 for v in opts):
  matches=[tuple(v[0] for v in opts)] # Retain explicit regional counts even if the source total differs.
 assert len(matches)==1,(y,areas,opts,totals)
 chosen.extend((a,y,n) for a,n in zip(areas,matches[0]))
annual=pl.DataFrame(chosen,schema=['area','year','fires'],orient='row')
annual.write_csv(OUT/'annual_resolved.csv')
from shapely import from_wkb
from shapely.strtree import STRtree
from shapely.ops import transform
from pyproj import Transformer
def geometry(b):
 envelope=(b[3]>>1)&7
 offset=8+{0:0,1:32,2:48,3:48,4:64}[envelope]
 return from_wkb(b[offset:])
gacc=pl.read_parquet(ROOT/'geo/gacc_2025.parquet').unique(['GACCUnitID','SHAPE'])
def state_name(s):
 if ' / ' in s:return s.split(' / ')[1]
 for pattern in (r'county in ([^,:]+)',r'Located in (.*?) \(',r'County — (.*?),'):
  m=re.search(pattern,s)
  if m:return m.group(1)
 return s.removesuffix(', United States').split(', ')[-1]
counties=pl.read_parquet(ROOT/'geo/usa_adm2.parquet').with_columns(pl.col('adm_description').map_elements(state_name,return_dtype=pl.String).alias('adm1_name1')).select('adm1_name1','geom').unique()
assert counties['adm1_name1'].null_count()==0

county_geoms=[geometry(b) for b in counties['geom']]
tree=STRtree(county_geoms)
area_map={'USAKACC':'Alaska','USCAONCC':'Northern California','USCAOSCC':'Southern California','USCORMC':'Rocky Mountains','USGASAC':'Southern Area','USMTNRC':'Northern Rockies','USNMSWC':'Southwest','USORNWC':'Northwest','USUTGBC':'Great Basin','USWIEACC':'Eastern Area'}
tr=Transformer.from_crs(4269,4326,always_xy=True)
links=[]
for r in gacc.iter_rows(named=True):
 geom=transform(tr.transform,geometry(r['SHAPE']))
 for idx in tree.query(geom,predicate='intersects'):
  links.append((counties['adm1_name1'][int(idx)],area_map[r['GACCUnitID']]))
links=pl.DataFrame(links,schema=['state','area'],orient='row').unique()
links.write_csv(OUT/'state_gacc.csv')
result=links.join(annual.group_by('area').agg(pl.col('fires').sum()),on='area').group_by('state').agg(pl.col('fires').sum()).sort('fires',descending=True)
result.write_csv(OUT/'state_totals.csv');print(result.head(10))
(OUT/'answer.json').write_text(json.dumps({'answer':result['state'][0]}))
