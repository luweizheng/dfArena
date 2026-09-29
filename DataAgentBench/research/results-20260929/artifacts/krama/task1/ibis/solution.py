import csv, io, re, json
from pathlib import Path
import ibis
import pyarrow as pa

out=Path('/workspace/work')
con=ibis.duckdb.connect()
docs=con.read_parquet('/workspace/data/domain_docs/files.parquet')
texts=docs.filter(docs.content.contains('Area\tReport')).to_pyarrow().to_pylist()
# Decode the embedded TSV and retain each dated narrative as a record.
pat=re.compile(r'\b(?:\d{4}[-/]\d{4}|\d{8}|\d{4}/\d{4}|[A-Za-z]+\d{2},\d{4}|\d{2}[A-Za-z]+-\d{4})\b')
rows=[]
for doc in texts:
    if 'Area\tReport\n' not in doc['content']: continue
    body=doc['content'].split('Area\tReport\n',1)[1]
    for row in csv.reader(io.StringIO(body),delimiter='\t'):
        if len(row)!=2: continue
        area, report=row
        for line in report.splitlines():
            m=pat.search(line)
            if m: rows.append({'area':area,'date_raw':m.group(),'line':line})

import pyarrow.parquet as pq
pq.write_table(pa.Table.from_pylist(rows), out/'parsed.parquet')
t=con.read_parquet(str(out/'parsed.parquet'), table_name='narratives')
# DuckDB try_strptime supports the source's compact and textual date formats.
con.raw_sql("CREATE VIEW dated AS SELECT *, CAST(try_strptime(date_raw, ['%Y%m%d','%Y-%m%d','%Y/%m%d','%m%d/%Y','%d%m/%Y','%b%d,%Y','%B%d,%Y','%d%b-%Y','%d%B-%Y']) AS DATE) AS reported FROM narratives")
t=con.table('dated').mutate(year=lambda x:x.reported.year())
t=t.filter(t.year.between(2020,2023))
# Resolve ambiguous numeric dates against the latest unambiguous report in each year.
u=t.filter(~t.date_raw.re_search(r'^\d{4}/\d{4}$') | t.date_raw.re_search(r'^20'))
caps=u.group_by('year').aggregate(cap=u.reported.max())
con.raw_sql("CREATE VIEW alternate AS SELECT *, CAST(try_strptime(date_raw, '%d%m/%Y') AS DATE) AS alt FROM dated")
a=con.table('alternate').mutate(year=lambda x:x.reported.year())
a=a.inner_join(caps,'year')
a=a.mutate(reported=ibis.greatest(ibis.ifelse(a.reported<=a.cap,a.reported,ibis.null().cast('date')), ibis.ifelse(a.alt<=a.cap,a.alt,ibis.null().cast('date'))))
a=a.filter(a.reported<=a.cap)
latest=a.group_by('area','year').aggregate(reported=a.reported.max())
x=a.inner_join(latest,['area','year','reported']).select(a.area,a.year,a.reported,a.date_raw,a.line).distinct()
records=x.order_by('area','year').to_pyarrow().to_pylist()
(out/'latest_reports.json').write_text(json.dumps(records,indent=2,default=str))
metric=r'(?:human-caused acres burned|human-ignited burn acreage|human-source acres consumed|acres burned by human-caused wildfires|acreage from human-caused fires)'
num=r'(?:\d{1,3}(?:[, ]\d{3})+|\d+|N/A)'
parsed=[]
for r in records:
    line=r['line']
    if not re.search(metric,line,re.I): continue
    # Number-before-label prose, label=value tables, and label-verb-number prose.
    matches=re.findall(r'('+num+r')\s+('+metric+r')',line,re.I)
    vals=[v for v,k in matches]
    if not vals:
        m=re.search(metric+r'(?:\s*\(|\s*(?:=|at)\s*|(?:\s+in\s+[^,]+?)?\s+(?:stood at|totaled|reached)\s*)('+num+r')',line,re.I)
        if m: vals=[m.group(1)]
    if not vals and 'respectively' in line:
        labels=re.findall(metric+r'|(?:lightning|human)[a-z -]+?(?:events|occurrences|incidents|wildfires)|fires from (?:human|lightning) causes',line,re.I)
        tail=re.split(r'\b(?:were|totaled)\b',line)[-1]
        numbers=re.findall(num,tail)
        for i,label in enumerate(labels):
            if re.fullmatch(metric,label,re.I) and i<len(numbers): vals.append(numbers[i])
    if not vals: raise ValueError(line)
    for v in vals:
        if v!='N/A': parsed.append({'area':r['area'],'year':r['year'],'explicit':int(not bool(re.fullmatch(r'\d{4}/\d{4}',r['date_raw'])) or r['date_raw'].startswith('20')),'acres':int(re.sub('[, ]','',v))})
pq.write_table(pa.Table.from_pylist(parsed),out/'acres.parquet')
f=con.read_parquet(str(out/'acres.parquet')).distinct()
priority=f.group_by('area','year').aggregate(explicit=f.explicit.max())
f=f.inner_join(priority,['area','year','explicit']).select(f).group_by('area','year').aggregate(acres=f.acres.max())
g=con.read_parquet('/workspace/data/geo/gacc_2025.parquet')
# Region names are normalized from the descriptions; abbreviations come from the data.
g=g.select(abbreviation=g.GACCDescription.re_extract(r'\b([A-Z]{4})\b',1),area=g.GACCDescription.re_extract(r'(Alaska|Eastern Area|Northern California|Northern Rockies|Northwest|Southern California|Southwest|Southern Area|Great Basin|Rocky Mountain)',1))
g=g.mutate(area=ibis.ifelse(g.area=='Rocky Mountain','Rocky Mountains',g.area)).distinct()
j=f.inner_join(g,'area')
result=j.group_by('abbreviation').aggregate(acres=j.acres.sum(),years=j.year.nunique()).order_by(ibis.desc('acres'))
r=result.to_pyarrow().to_pylist()
print(r)
assert all(i['years']==4 for i in r)
(out/'totals.json').write_text(json.dumps(r,indent=2))
(out/'answer.json').write_text(json.dumps({'answer':r[0]['abbreviation']}))
