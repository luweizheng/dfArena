from datetime import datetime
import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
p = con.read_parquet('/workspace/data/publication/publicationinfo.parquet')
d = con.read_parquet('/workspace/data/CPCDefinition/cpc_definition.parquet')

@ibis.udf.scalar.builtin
def try_strptime(s: str, formats: list[str]) -> datetime:
    ...

def parse_date(col):
    clean = (col.lower().re_replace(r'(\d)(st|nd|rd|th)\b', r'\1')
             .re_replace(r'\b(dated|on|the|of)\b', '')
             .replace(',', ' ').re_replace(r'\s+', ' ').strip())
    return try_strptime(clean, ['%d %B %Y','%d %b %Y','%B %d %Y','%b %d %Y',
                                '%Y %B %d','%Y %b %d']).date()

# Publication identifiers encode the country; avoid matching DE in assignee names.
p = p.mutate(patent=p.Patents_info.re_extract(r'((?:[A-Z]{2})-[0-9]+-[A-Z][0-9])\b', 1))
p = p.filter(p.patent.startswith('DE-')).mutate(granted=parse_date(p.grant_date), filed=parse_date(p.filing_date))
print('Unparsed German grant dates:', p.filter(p.grant_date.notnull() & p.granted.isnull()).select('grant_date').distinct().to_pyarrow().to_pylist())
p = p.filter(p.granted.between(ibis.date('2019-07-01'), ibis.date('2019-12-31')))
print('Selected publications:', p.count().execute())
assert p.filter(p.filed.isnull()).count().execute() == 0
p = p.select('patent', year=p.filed.year(), entry=p.cpc.cast('json').cast('array<struct<code: string, first: boolean, inventive: boolean, tree: array<string>>>').unnest())
p = p.filter(p.entry['first']).select('patent','year',group=p.entry['code'].substr(0,3)).distinct()
defs = d.filter(d.level == 4).select(group=d.symbol, title=d.titleFull).distinct()
counts = p.join(defs, 'group').group_by('group','title','year').aggregate(filings=ibis._.patent.nunique())
bounds = counts.group_by('group','title').aggregate(start=counts.year.min(),end=counts.year.max())
grid = bounds.select('group','title',year=ibis.range(bounds.start,bounds.end+1).unnest())
s = grid.left_join(counts, ['group','title','year']).select(grid.group,grid.title,grid.year,filings=counts.filings.fill_null(0))
# Unadjusted EMA: first observation initializes the series, then E_t=.1*x_t+.9*E_(t-1).
# Compute the equivalent weighted sum lazily with a self join.
s = s.mutate(start=s.year.min().over(ibis.window(group_by='group')))
h = s.view()
v = s.join(h, (s.group==h.group)&(h.year<=s.year))
ema = v.group_by(s.group,s.title,s.year).aggregate(ema=(h.filings * ibis.ifelse(h.year==h.start,1.0,0.1) * (ibis.literal(0.9)**(s.year-h.year))).sum())
ema = ema.mutate(ema=ema.ema.round(12))
ranked = ema.mutate(rank=ibis.row_number().over(ibis.window(group_by='group',order_by=[ibis.desc('ema'),'year'])))
best = ranked.filter(ranked.rank==0).order_by(ibis.desc('ema'),'group').select('title','group','ema',best_year=ranked.year)
rows = best.to_pyarrow().to_pylist()
(OUT/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
answer = 'Peak annual EMA (α=0.1; initialized with the first year’s count):\n' + '\n'.join(f"{r['group']} — {r['title']} — {r['best_year']} (EMA {r['ema']:.3f})" for r in rows)
(OUT/'answer.json').write_text(json.dumps({'answer':answer},ensure_ascii=False))
print(answer)
