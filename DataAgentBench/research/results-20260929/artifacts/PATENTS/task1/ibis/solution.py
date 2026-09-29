import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
p = con.read_parquet('/workspace/data/publication/publicationinfo.parquet')
d = con.read_parquet('/workspace/data/CPCDefinition/cpc_definition.parquet')
# Level 5 symbols are CPC subclasses: the first four characters of a code.
level5 = d.filter(d.level == 5).select(group=d.symbol).distinct()
base = p.select(
    patent=p.Patents_info,
    year=p.filing_date.re_extract(r'\b((?:18|19|20)\d{2})\b', 1).nullif('').cast('int64'),
    entries=p.cpc.cast('json').cast('array<struct<code: string, first: boolean, inventive: boolean, tree: array<string>>>'),
)
base = base.filter(base.year.notnull()).select('patent', 'year', entry=base.entries.unnest())
primary = base.filter(base.entry['first'] == True).select(
    'patent', 'year', group=base.entry['code'].substr(0,4)
).distinct()
primary = primary.semi_join(level5, 'group')
counts = primary.group_by('group', 'year').aggregate(filings=primary.count())
bounds = counts.group_by('group').aggregate(first_year=counts.year.min(), last_year=counts.year.max())
grid = bounds.select('group', 'first_year', year=ibis.range(bounds.first_year, bounds.last_year+1).unnest())
annual = grid.left_join(counts, ['group','year']).select(grid.group, grid.year, grid.first_year, filings=counts.filings.fill_null(0))
# EMA_0 = filings_0; EMA_t = .2 * filings_t + .8 * EMA_(t-1).
# Weighted cumulative sum is algebraically equivalent to that recurrence.
annual = annual.mutate(age=annual.year-annual.first_year)
annual = annual.mutate(weighted=ibis.ifelse(annual.age==0, annual.filings, .2*annual.filings) / (.8**annual.age))
w = ibis.window(group_by=annual.group, order_by=annual.year, preceding=None, following=0)
ema = annual.mutate(ema=(annual.weighted.sum().over(w) * (.8**annual.age)).round(12))
r = ibis.window(group_by=ema.group, order_by=[ema.ema.desc(), ema.year.asc()])
best = ema.mutate(rank=ibis.row_number().over(r)).filter(lambda t: (t.rank==0) & (t.year==2022)).select('group').order_by('group')
rows = best.to_pyarrow().to_pylist()
answer = ', '.join(row['group'] for row in rows)
(OUT/'answer.json').write_text(json.dumps({'answer': answer})+'\n')
# Persist the compact annual series for reproducible inspection.
ema.order_by('group','year').to_parquet(OUT/'annual_ema.parquet')
print(json.dumps({'answer': answer}))
