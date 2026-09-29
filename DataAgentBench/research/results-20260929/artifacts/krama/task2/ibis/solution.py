import ibis, pyarrow as pa, json, re, csv, io
from pathlib import Path
import shapely
OUT=Path('/workspace/work')
c=ibis.duckdb.connect()
docs=c.read_parquet('/workspace/data/domain_docs/files.parquet')
rows=[]
# Decode narrative records, leaving date conversion and report selection to DuckDB.
pat=r'(?:\d{4}[-/]\d{4}|\d{4}/\d{2,4}|\d{8}|\d{6}|\d{1,2}[A-Za-z]+-\d{2,4}|[A-Za-z]+\d{1,2},\d{2,4})'
for d in docs.filter(docs.content.contains('Area\tReport')).to_pyarrow().to_pylist():
 text=d['content'];text=text[text.index('Area\tReport'):]
 for row in csv.DictReader(io.StringIO(text),delimiter='\t'):
  for line in (row.get('Report') or '').splitlines():
   # Dates occur in explicit wrappers at either the beginning or end.
   m=re.search(r'\(reported (.*?)\)\s*$',line)
   token=m.group(1) if m else None
   if token is None:
    m=re.match(r'(?:As of |Date: |\[|\()?('+pat+r')',line)
    if m: token=m.group(1)
   if token: rows.append({'area':row['Area'],'raw_date':token,'line':line})
print('parsed',len(rows), rows[:1], pa.Table.from_pylist(rows).schema)
import pyarrow.parquet as pq
pq.write_table(pa.Table.from_pylist(rows),OUT/'reports.parquet')
c.read_parquet(str(OUT/'reports.parquet'),table_name='reports')
formats=['%Y%m%d','%Y/%m%d','%Y-%m%d','%d%b-%Y','%B%d,%Y','%b%d,%Y','%m%d/%y','%d%m/%y','%d%b-%y','%B%d,%y','%b%d,%y','%y%m%d']
expr='coalesce('+','.join("try_strptime(raw_date, '"+f+"')" for f in formats)+')::DATE'
unamb=c.sql('select *, '+expr+' as date from reports')
unamb=unamb.mutate(year=unamb.date.year()).filter(lambda t:t.year.between(2014,2024))
latest=unamb.group_by('year').aggregate(date=unamb.date.max())
# For numeric month/day tokens consider both conventions, then match the
# latest annual report date established by unambiguous date spellings.
r=c.sql("select *, "+expr+" as date from reports UNION ALL select *, try_strptime(raw_date, '%m%d/%Y')::DATE as date from reports UNION ALL select *, try_strptime(raw_date, '%d%m/%Y')::DATE as date from reports")
r=r.mutate(year=r.date.year())
s=r.join(latest,['year','date']).select(r.area,r.year,r.date,r.line).distinct()
selected=s.to_pyarrow().to_pylist()
(OUT/'latest_lines.json').write_text(json.dumps(selected,default=str,indent=2))
print('latest records',len(selected))

metric=r'(?:lightning-caused wildfires|lightning-ignited fire events|lightning-caused fire occurrences|lightning-source wildfire incidents|fires from lightning causes)'
num=r'(?:\d{1,3}(?:[, ]\d{3})+|\d+|N/A)'
facts=[];unparsed=[]
for row in selected:
 line=re.sub(r'acres burned by lightning-caused wildfires','LIGHTNING_ACRES',row['line'],flags=re.I); val=None
 if not re.search(metric,line,re.I): continue
 # Numeric values before the metric, or metric followed by its value.
 m=re.search('('+num+r')\s+'+metric,line,re.I)
 if m: val=m.group(1)
 else:
  m=re.search(metric+r'(?:\s+in\s+[A-Za-z ]+)?\s*(?:=|\(|reached|totaled|stood at|at)\s*('+num+')',line,re.I)
  if m:val=m.group(1)
  else:
   m=re.search(metric+r' and .*? were ('+num+r') and ',line,re.I)
   if m:val=m.group(1)
 if val is None:
  m=re.search(r'and '+metric+r' in .*? were '+num+r' and ('+num+r'), respectively',line,re.I)
  if m: val=m.group(1)
 if val is None:unparsed.append(row)
 if val is not None and val!='N/A': facts.append({'area':row['area'],'year':row['year'],'fires':int(re.sub('[, ]','',val))})
print('unparsed',unparsed)
assert not unparsed
pq.write_table(pa.Table.from_pylist(facts),OUT/'facts.parquet')
f=c.read_parquet(str(OUT/'facts.parquet')).distinct()
# Compact MMDD/DDMM dates can also identify an earlier report. Annual
# cumulative counts resolve duplicate candidates in favor of the year-end total.
f=f.group_by('area','year').aggregate(fires=f.fires.max())
assert f.filter(f.area.isin(list(['Alaska','Eastern Area','Northern California','Southern California','Northern Rockies','Northwest','Southwest','Southern Area','Great Basin','Rocky Mountains']))).count().execute()==110
print('coverage',f.group_by('area').aggregate(years=f.count(),fires=f.fires.sum()).to_pyarrow().to_pylist())
# GeoPackage headers are decoded only at the geometry boundary.
def decode(b):
 assert b[:2]==b'GP'
 env=(b[3]>>1)&7
 return shapely.from_wkb(b[8+{0:0,1:32,2:48,3:48,4:64}[env]:])
g=c.read_parquet('/workspace/data/geo/gacc_2025.parquet')
gs=g.select('GACCUnitID','SHAPE').distinct().to_pyarrow().to_pylist()
area_map={'USAKACC':'Alaska','USWIEACC':'Eastern Area','USCAONCC':'Northern California','USCAOSCC':'Southern California','USMTNRC':'Northern Rockies','USORNWC':'Northwest','USNMSWC':'Southwest','USGASAC':'Southern Area','USUTGBC':'Great Basin','USCORMC':'Rocky Mountains'}
print('units',sorted(set(x['GACCUnitID'] for x in gs)))
geoms=[decode(x['SHAPE']) for x in gs];tree=shapely.STRtree(geoms)
u=c.read_parquet('/workspace/data/geo/usa_adm2.parquet')
states='Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|District of Columbia|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming'
# State names are embedded in several documented prose templates.
d=u.adm_description
state=ibis.cases((d.contains(' / '),d.split(' / ')[1]),(d.contains('is a county in '),d.re_extract(r'is a county in (.*?),',1)),(d.startswith('Located in '),d.re_extract(r'Located in (.*?) \(',1)),(d.startswith('A county in '),d.re_extract(r'A county in (.*?):',1)),(d.contains(' — '),d.re_extract(r' — (.*?),',1)),else_=d.re_extract(r', ('+states+r')(?:,|$)',1))
u=u.mutate(state=state).select('state','geom').distinct()
pairs=[]
for row in u.to_pyarrow().to_pylist():
 assert row['state'],row
 for idx in tree.query(decode(row['geom']),predicate='intersects'):
  pairs.append({'state':row['state'],'area':area_map[gs[idx]['GACCUnitID']]})
pq.write_table(pa.Table.from_pylist(pairs),OUT/'intersections.parquet')
p=c.read_parquet(str(OUT/'intersections.parquet')).distinct()
tot=f.group_by('area').aggregate(fires=f.fires.sum())
joined=p.join(tot,'area')
ranking=joined.group_by('state').aggregate(fires=joined.fires.sum()).order_by(ibis.desc('fires'))
result=ranking.to_pyarrow().to_pylist()
print(result[:10]);(OUT/'ranking.json').write_text(json.dumps(result,indent=2))
(OUT/'answer.json').write_text(json.dumps({'answer':result[0]['state']}))
