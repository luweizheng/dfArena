import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
c = ibis.duckdb.connect()

def code(s):
    return s.re_extract(r'(\d+)', 1).try_cast('int64')

def name(s):
    return s.lower().re_replace(r'[^a-z0-9]', '')

# Only the year is needed for inclusive whole-calendar-year filtering.
def year(s):
    four = s.re_extract(r'\b((?:19|20)\d{2})(?:\d{4}(?:T|\d| )|\b)', 1).nullif('').try_cast('int64')
    short = s.re_extract(r'\b(\d{2})(?:\d{10}\b|-\d{2}-\d{2} )', 1).nullif('').try_cast('int64')
    return four.coalesce(2000 + short)

t = c.read_parquet('/workspace/data/geo/beach_water_temperature.parquet')
v = t.water_temp.re_extract(r'([-+]?\d+(?:\.\d+)?)', 1).try_cast('float64')
u = t.water_temp.lower()
temp = ibis.cases((u.contains('f'), (v-32)*5/9), (u.re_search(r'k\s*$'), v-273.15), else_=v)
t = t.mutate(community=code(t.community_code), county=code(t.county_code), beach=name(t.beach_name), year=year(t.sample_date), celsius=temp)
assert t.filter(t.year.isnull() | t.celsius.isnull()).count().execute() == 0
t = t.filter(t.year.between(2008, 2016))
ranked = t.group_by('community','county','beach').aggregate(beach_name=t.beach_name.min(), mean_celsius=t.celsius.mean(), readings=t.celsius.count()).order_by('mean_celsius')
winner = ranked.limit(1)
print('Lowest averages:', ranked.limit(5).to_pyarrow().to_pylist())

d = c.read_parquet('/workspace/data/domain_docs/files.parquet')
d = d.filter(d.content.contains('Community Code\tCounty Code\tLocation\tResult'))
r = d.select(line=d.content.split('\n').unnest())
r = r.filter(r.line.re_search(r'^[^\t]+\t[^\t]+\t[^\t]+\t'))
p = r.line.split('\t')
r = r.select(community=code(p[0]), county=code(p[1]), location=p[2], result=p[3])
r = r.filter(r.community.notnull())
# Extract beach names from the source's eight prose templates.
patterns = [
 r'^On .+?, a water sample was taken at (.+) \((?:Marine|Fresh) beach\)',
 r'^Sample collected at (.+) \((?:Marine|Fresh)\) in ',
 r'^Water sample from (.+) — a (?:Marine|Fresh) beach',
 r'^Location: (.+?), [^,]+, [^.]+\. Beach type:',
 r'^(.+) is a (?:Marine|Fresh) beach in ',
 r'^(.+) \((?:Marine|Fresh) beach, .+\) was sampled on ',
 r'^[^:]+: (.+) \((?:Marine|Fresh) beach\), sampled on ',
 r'water sample at (.+) \((?:Marine|Fresh)\),',
]
beach = ibis.coalesce(*[r.location.re_extract(p,1).nullif('') for p in patterns])
r = r.mutate(beach=name(beach), year=year(r.location))
assert r.filter(r.beach.isnull()).count().execute() == 0
joined = r.inner_join(winner, ['community','county','beach']).select(r, winner.beach_name, winner.mean_celsius)
assert joined.filter(joined.year.isnull()).count().execute() == 0
j = joined.filter(joined.year.between(2008,2016))
# Explicit outcome language, rather than inferring from organism thresholds.
positive = r'failed|exceed|non-compliant|constitutes a violation|surpassed|violation recorded|quality violation'
negative = r'within|met water quality|meeting all|\bpassed\b|; compliant|no violation|no quality violation'
j = j.mutate(violation=j.result.lower().re_search(positive) & ~j.result.lower().re_search(negative))
assert j.filter(~j.result.lower().re_search(positive) & ~j.result.lower().re_search(negative)).count().execute() == 0
print('Violations:', j.filter(j.violation).select('location','result').to_pyarrow().to_pylist())
summary = j.aggregate(samples=j.count(), violations=j.violation.cast('int64').sum())
result = summary.mutate(rate=100.0*summary.violations/summary.samples).to_pyarrow().to_pylist()[0]
assert result['samples'] > 0
print(result)
selected = winner.to_pyarrow().to_pylist()[0]
(OUT/'answer.json').write_text(json.dumps({'answer': f"{selected['beach_name']}: {result['rate']:.2f}%."}))
(OUT/'calculation.json').write_text(json.dumps({'beach':selected, **result}, indent=2))
