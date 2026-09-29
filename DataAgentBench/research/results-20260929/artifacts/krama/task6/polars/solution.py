import json,re,io
from pathlib import Path
import polars as pl
ROOT=Path('/workspace/data')
OUT=Path('/workspace/work')

def norm(e):
    return e.str.to_lowercase().str.replace_all(r'[^a-z0-9]','')

def year_of_location(s):
    # Compact datetimes use YYYYMMDD or YYMMDD, followed by time.
    m=re.search(r'(?<!\d)(\d{8}T\d{6}|\d{14}|\d{12}|\d{8})(?!\d)',s)
    if m:
        x=m.group(1)
        return 2000+int(x[:2]) if len(x)==12 else int(x[:4])
    m=re.search(r'\b(20\d{2}|19\d{2})\b',s)
    if m: return int(m.group(1))
    m=re.search(r'\b(\d{2})-\d{2}-\d{2}\b',s)
    if m: return 2000+int(m.group(1))
    raise ValueError(s)

t=pl.read_parquet(ROOT/'geo/beach_water_temperature.parquet')
t=t.with_columns(pl.col('sample_date').str.extract(r'(20\d{2}|19\d{2})').cast(pl.Int32).alias('year'),pl.col('water_temp').str.extract(r'([-+]?\d+(?:\.\d+)?)').cast(pl.Float64).alias('value'),pl.col('community_code').str.extract(r'(\d+)').cast(pl.Int32).alias('community'),pl.col('county_code').str.extract(r'(\d+)').cast(pl.Int32).alias('county'),norm(pl.col('beach_name')).alias('beach'))
t=t.with_columns(pl.when(pl.col('water_temp').str.contains(r'(?i)f')).then((pl.col('value')-32)*5/9).when(pl.col('water_temp').str.contains(r'(?i)k')).then(pl.col('value')-273.15).otherwise(pl.col('value')).alias('celsius'))
assert t['year'].null_count()==0 and t['celsius'].null_count()==0
ranking=t.filter(pl.col('year').is_between(2008,2016)).group_by('community','county','beach').agg(pl.col('celsius').mean(),pl.len().alias('readings'),pl.col('beach_name').first()).sort('celsius')
ranking.write_csv(OUT/'temperature_ranking.csv')
w=ranking.row(0,named=True)
frames=[]
header='Community Code\tCounty Code\tLocation\tResult'
for s in pl.read_parquet(ROOT/'domain_docs/files.parquet')['content']:
    if header in s:
        frame=pl.read_csv(io.StringIO(s[s.index(header):]),separator='\t',infer_schema=False)
        frames.append(frame)
b=pl.concat(frames).with_columns(pl.col('Community Code').str.extract(r'(\d+)').cast(pl.Int32).alias('community'),pl.col('County Code').str.extract(r'(\d+)').cast(pl.Int32).alias('county'),norm(pl.col('Location')).alias('normalized_location'))
b=b.filter((pl.col('community')==w['community'])&(pl.col('county')==w['county'])&pl.col('normalized_location').str.contains(w['beach'],literal=True))
b=b.with_columns(pl.col('Location').map_elements(year_of_location,return_dtype=pl.Int32).alias('year'))
positive=r'exceed|failed|surpassed|constitutes a violation|in violation|violation of'
negative=r'within|\bpassed\b|met water|meeting all|compliant|no violation|no quality violation'
b=b.with_columns(pl.col('Result').str.contains(positive).alias('violation'),pl.col('Result').str.contains(negative).alias('pass'))
assert b.filter(~pl.col('violation')&~pl.col('pass')).height==0
assert b.filter(pl.col('violation')&pl.col('pass')).height==0
b=b.filter(pl.col('year').is_between(2008,2016))
b.write_csv(OUT/'selected_bacterial_samples.csv')
n=b.height; v=b['violation'].sum(); rate=v/n*100
answer=f"{w['beach_name']}: {rate:.2f}% ({v} violations out of {n} samples)."
(OUT/'answer.json').write_text(json.dumps({'answer':answer}))
print(w);print(answer)
