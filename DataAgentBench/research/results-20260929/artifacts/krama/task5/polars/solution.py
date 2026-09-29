import re,json
import polars as pl
from pathlib import Path
BASE=Path('/workspace/data')
def canon(s): return re.sub('[^a-z0-9]','',s.lower())
def code(s): return int(re.search(r'\d+',s).group())
def year(s):
    m=re.search(r'(?<!\d)((?:19|20)\d{2})',s)
    if m:return int(m[1])
    m=re.search(r'(?<!\d)(\d{2})(?:-\d{2}-\d{2}|\d{10})(?!\d)',s)
    if m:return 2000+int(m[1])
    raise ValueError(s)
patterns=[r'^(.+?) \((?:Fresh|Marine) beach,',r'^[^:]+: (.+?) \((?:Fresh|Marine) beach\), sampled',r'water sample at (.+?) \((?:Fresh|Marine)\),',r'was taken at (.+?) \((?:Fresh|Marine) beach\) in',r'^Location: (.+), [^,]+, [^.]+\. Beach type:',r'^(.+?) is a (?:Fresh|Marine) beach in',r'^Water sample from (.+?) — a',r'^Sample collected at (.+?) \((?:Fresh|Marine)\) in']
def beach(s):
 for p in patterns:
  m=re.search(p,s)
  if m:return canon(m[1])
 raise ValueError(s)
rows=[]
for s in pl.read_parquet(BASE/'domain_docs/files.parquet')['content']:
 if 'Community Code\tCounty Code\tLocation\tResult' not in s:continue
 for line in s.splitlines():
  a=line.split('\t')
  if len(a)!=4 or a[0]=='Community Code':continue
  failed=bool(re.search(r'exceeded|failed to meet|constitutes a violation|non-compliant|exceeding|did not meet|surpassed|; violation recorded',a[3]))
  if failed:rows.append((code(a[0]),code(a[1]),beach(a[2]),year(a[2])))
f=pl.DataFrame(rows,schema=['community','county','beach','year'],orient='row')
ranking=f.filter(pl.col('year').is_between(2012,2018)).group_by('community','county','beach').len().sort('len',descending=True)
print(ranking.head(10))
assert ranking['len'][0]>ranking['len'][1]
winner=ranking.head(1).drop('len')
t=pl.read_parquet(BASE/'geo/beach_water_temperature.parquet').with_columns(pl.col('community_code').map_elements(code,return_dtype=pl.Int64).alias('community'),pl.col('county_code').map_elements(code,return_dtype=pl.Int64).alias('county'),pl.col('beach_name').map_elements(canon,return_dtype=pl.String).alias('beach'))
t=t.join(winner,on=['community','county','beach']).with_columns(pl.col('sample_date').map_elements(year,return_dtype=pl.Int64).alias('year')).filter(pl.col('year').is_between(2012,2018))
print(t.select('beach_name','sample_date','water_temp'))
v=pl.col('water_temp').str.extract(r'(-?\d+(?:\.\d+)?)',1).cast(pl.Float64)
s=pl.col('water_temp').str.to_lowercase()
t=t.with_columns(pl.when(s.str.contains('f')).then((v-32)*5/9).when(s.str.contains('k')).then(v-273.15).otherwise(v).alias('celsius'))
avg=t['celsius'].mean()
assert avg is not None
print('count',t.height,'mean',avg)
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':f'{avg:.2f} °C'}))
ranking.write_csv('/workspace/work/failure_counts.csv')
t.write_csv('/workspace/work/selected_temperatures.csv')
