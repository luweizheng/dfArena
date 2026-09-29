import json
from pathlib import Path
import ibis
from check import normalize

@ibis.udf.scalar.python
def cve_candidates(value: str) -> list[str]:
    return sorted(normalize(value)) if value else []

con=ibis.duckdb.connect()
def table(path):return con.read_parquet('/workspace/data/'+path+'.parquet')
scores=table('vulns_db/cvss_metadata')
matches=table('cpe_db/cpe_matches')
aliases=table('cpe_db/vendor_aliases')
kev=table('kev_db/kev_entries')
# Parse each vendor surface form from the three product identifier formats.
vendor=ibis.ifelse(matches.criteria.startswith('cpe:2.3:'),matches.criteria.split(':')[3],matches.criteria.re_extract(r'^([^/ ]+)',1))
matches=matches.mutate(alias=vendor).join(aliases.filter(aliases.canonical_vendor=='microsoft'),'alias').filter(lambda t:t.vulnerable_flag.lower().strip().isin(['1','t','true','y','yes','v','vulnerable','affected']))
m=matches.select('cve_id').distinct().mutate(candidates=lambda t:cve_candidates(t.cve_id))
s=scores.mutate(score=scores.score_text.re_extract(r'([0-9]+(?:\.[0-9]+)?)',1).cast('decimal(10,4)')).filter(lambda t:t.score>=7).mutate(candidates=lambda t:cve_candidates(t.cve_id))
k=kev.mutate(candidates=cve_candidates(kev.cve_ref),reference=kev.notes.re_extract(r'nvd\.nist\.gov/vuln/detail/(CVE-[0-9]{4}-[0-9]+)',1))
# KEV notes provide an independent identifier to disambiguate encodings.
k=k.mutate(cve=k.candidates.unnest()).filter(lambda t:(t.reference=='')|t.reference.isnull()|(t.cve==t.reference)).select('cve').distinct()
mm=m.mutate(cve=m.candidates.unnest())
ss=s.mutate(cve=s.candidates.unnest())
result=k.join(mm.select('cve').distinct(),'cve').join(ss.select('cve').distinct(),'cve').select('cve').distinct()
count=int(result.count().execute())
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(count)}))
# Materialize diagnostics only after the relational filters and joins.
for name,t in [('matching_cves',result),('microsoft_candidates',mm.join(k,'cve')),('score_candidates',ss.join(k,'cve'))]:
 Path('/workspace/work/'+name+'.json').write_text(json.dumps(t.to_pyarrow().to_pylist(),default=str))
print(count)
