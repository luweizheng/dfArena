import json, re
from pathlib import Path
from datetime import datetime
import ibis
import pyarrow as pa

OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
@ibis.udf.scalar.builtin
def try_strptime(value: str, fmt: str) -> datetime: ...

def parse_date(x, formats):
    return ibis.coalesce(*[
        ibis.ifelse(x.re_search(r'^\d{14}$'), try_strptime(x,f), ibis.null()) if f == '%Y%m%d%H%M%S' else
        ibis.ifelse(x.re_search(r'^\d{12}$'), try_strptime(x,f), ibis.null()) if f == '%y%m%d%H%M%S' else
        try_strptime(x,f) for f in formats])

def keys(t):
    return t.mutate(community=t.community_code.re_extract(r'(\d+)',1).cast('int'),county=t.county_code.re_extract(r'(\d+)',1).cast('int'),beach=t.beach_name.lower().re_replace('[^a-z0-9]',''))

docs=con.read_parquet('/workspace/data/domain_docs/files.parquet')
header='Community Code\tCounty Code\tLocation\tResult'
docs=docs.filter(docs.content.contains(header))
# Decode the prose representation; all relational operations follow in Ibis.
patterns=[
 r'^On (.*?), a water sample was taken at (.*?) \((?:Fresh|Marine) beach\) in ',
 r'^Water sample from (.*?) — a (?:Fresh|Marine) beach in .*? — collected on (.*?)\.$',
 r'^(.*?) is a (?:Fresh|Marine) beach in .*?\. Sample collected on (.*?)\.$',
 r'^(.*?) \((?:Fresh|Marine) beach, .*?\) was sampled on (.*?)\.$',
 r'^Sample collected at (.*?) \((?:Fresh|Marine)\) in .*? on (.*?)\.$',
 r'^Location: (.*?), [^,]+, [^.]+\. Beach type: (?:Fresh|Marine)\. Sample date: (.*?)\.$',
 r'^[^,]+, [^:]+: (.*?) \((?:Fresh|Marine) beach\), sampled on (.*?)\.$',
 r'^(.*?): water sample at (.*?) \((?:Fresh|Marine)\), ',
]
rows=[]
for doc in docs.to_pyarrow().to_pylist():
    for line in doc['content'].split(header,1)[1].strip().splitlines():
        if not line.strip(): continue
        if line.startswith("(source:"): continue
        if len(line.split("\t")) != 4: raise ValueError(repr(line))
        cc,co,loc,result=line.split('\t')
        for i,pattern in enumerate(patterns):
            m=re.search(pattern,loc)
            if m:
                a,b=m.groups(); date,beach=(a,b) if i in (0,7) else (b,a)
                rows.append(dict(community_code=cc,county_code=co,beach_name=beach,sample_date=date,result=result))
                break
        else: raise ValueError(loc)
import pyarrow.parquet as pq
pq.write_table(pa.Table.from_pylist(rows), OUT/'bacteria.parquet')
b=con.read_parquet(str(OUT/'bacteria.parquet'))
b=keys(b)
b=b.mutate(date=parse_date(b.sample_date,['%Y%m%dT%H%M%S','%Y%m%d%H%M%S','%y%m%d%H%M%S','%Y%m%d %H-%M-%S','%y-%m-%d %H-%M-%S','%Y-%m-%d %H:%M:%S','%B %d, %Y %H:%M:%S','%d %b %Y %H:%M:%S']))
assert b.filter(b.date.isnull()).count().execute()==0
fail=r'failed to meet|did not meet|constitutes a violation|; violation recorded|non-compliant|exceeded the limit|surpassed the regulatory threshold|exceeding acceptable limits'
print('result templates',b.select(r=b.result.re_replace(r'[0-9.]+','N')).distinct().to_pyarrow().to_pylist())
b=b.filter(b.date.year().between(2012,2018),b.result.re_search(fail))
rank=b.group_by('community','county','beach').aggregate(failures=b.count()).order_by(ibis.desc('failures'))
print('ranking',rank.limit(10).to_pyarrow().to_pylist())
winner=rank.limit(1)
t=keys(con.read_parquet('/workspace/data/geo/beach_water_temperature.parquet'))
t=t.mutate(date=parse_date(t.sample_date,['%Y-%m-%d','%Y/%m/%d','%d-%m-%Y','%m/%d/%Y','%d/%m/%Y','%B %d, %Y','%b %d, %Y','%d %B %Y','%d %b %Y']))
print('unparsed dates',t.filter(t.date.isnull()).select('sample_date').distinct().to_pyarrow().to_pylist())
assert t.filter(t.date.isnull()).count().execute()==0
t=t.filter(t.date.year().between(2012,2018)).inner_join(winner,['community','county','beach'])
v=t.water_temp.re_extract(r'([-+]?\d+(?:\.\d+)?)',1).try_cast('float64')
u=t.water_temp.lower()
t=t.mutate(celsius=ibis.cases((u.contains('f'),(v-32)*5/9),(u.re_search(r'k|kelvin'),v-273.15),else_=v))
print('selected temperatures',t.select('beach_name','sample_date','water_temp','celsius').to_pyarrow().to_pylist())
r=t.aggregate(mean=t.celsius.mean(),n=t.celsius.count()).to_pyarrow().to_pylist()[0]
assert r['n']>0
answer=f"{r['mean']:.2f} °C"
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(answer)
