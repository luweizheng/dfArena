import json
from datetime import date
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
# All natural-language dates carry an unambiguous year and named month.
p = pl.scan_parquet('/workspace/data/publication/publicationinfo.parquet').select('Patents_info','filing_date','grant_date','cpc').filter(
    pl.col('Patents_info').str.extract(r'\b([A-Z]{2})-\d+',1) == 'DE'
).filter(
    pl.col('grant_date').str.contains(r'\b2019\b') &
    pl.col('grant_date').str.contains(r'(?i)\b(?:Jul\w*|Aug\w*|Sep\w*|Oct\w*|Nov\w*|Dec\w*)\b')
).collect().with_columns(
    pl.col('Patents_info').str.extract(r'\b(DE-\d+-[A-Z]\d*)\b',1).alias('patent'),
    pl.col('filing_date').str.extract(r'\b(\d{4})\b',1).cast(pl.Int32).alias('year'),
    pl.col('cpc').str.json_decode(pl.List(pl.Struct({'code':pl.String,'first':pl.Boolean,'inventive':pl.Boolean,'tree':pl.List(pl.String)}))).alias('codes')
)
assert p['patent'].null_count()==0 and p['year'].null_count()==0
c = (p.select('patent','year','codes').explode('codes').unnest('codes')
     .filter(pl.col('first')==True).with_columns(pl.col('code').str.slice(0,3).alias('group'))
     .select('patent','year','group').unique())
d = pl.read_parquet('/workspace/data/CPCDefinition/cpc_definition.parquet',columns=['symbol','level','titleFull']).filter(pl.col('level')==4).select(pl.col('symbol').alias('group'),'titleFull').unique()
c = c.join(d.select('group'),on='group',how='inner')
counts=c.group_by('group','year').agg(pl.len().alias('filings'))
grid=counts.group_by('group').agg(pl.int_ranges(pl.col('year').min(),pl.col('year').max()+1).alias('year')).explode('year').with_columns(pl.col('year').cast(pl.Int32))
series=grid.join(counts,on=['group','year'],how='left').with_columns(pl.col('filings').fill_null(0)).sort('group','year').with_columns(pl.col('filings').ewm_mean(alpha=0.1,adjust=False).over('group').alias('ema'))
best=series.sort(['group','ema','year'],descending=[False,True,False]).unique(subset='group',keep='first').join(d,on='group').sort(['ema','group'],descending=[True,False])
series.write_csv(OUT/'annual_ema.csv')
best.write_csv(OUT/'best_years.csv')
lines=[f"{r['group']} — {r['titleFull']} — {r['year']}" for r in best.iter_rows(named=True)]
answer='Best year for each level-4 CPC group (Germany; grants July–December 2019; annual EMA α=0.1, initialized with the first annual count; zero-filing years included):\n'+'\n'.join(lines)
(OUT/'answer.json').write_text(json.dumps({'answer':answer},ensure_ascii=False))
print(f'Filtered publications: {p.height}; distinct patent/group pairs: {c.height}; groups: {best.height}')
print(best.select('group','year','ema'))
