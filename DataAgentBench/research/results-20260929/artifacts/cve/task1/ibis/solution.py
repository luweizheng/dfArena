import ibis, re, json
from pathlib import Path
ROOT=Path('/workspace/data');OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
def table(p):return con.read_parquet(str(ROOT/p))
kev=table('kev_db/kev_entries.parquet')
# The explicit NVD detail URL provides an unambiguous canonical identifier for
# each KEV record, independent of the noisy cve_ref encoding.
kev=kev.mutate(cid=kev.notes.re_extract(r'(?i)nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)',1).upper())
assert kev.filter(kev.cid.isnull()|(kev.cid=='')).count().execute()==0
ids=kev.select('cid').distinct().to_pyarrow().column('cid').to_pylist()
def b36(n):
 s=''; chars='0123456789abcdefghijklmnopqrstuvwxyz'
 while n:n,r=divmod(n,36);s=chars[r]+s
 return s or '0'
def forms(cid):
 _,ys,ns=cid.split('-');y=int(ys);n=int(ns);ns=f'{n:04d}';p=f'{n:07d}';q=ns;yy=ys[2:];cc=ys[:2]
 inter=''.join(a+b for a,b in zip(ys,p[:4]))+p[4:]
 fs=[f'CVE-{ys}-{ns}',f'cve-{ys}-{ns}',f'CVE_{ys}_{ns}',f'cve:{ys}:{ns}',f'{ys}-{ns}',f'{ys}_{ns}',f'{ys}:{ns}',f'{ys}::{ns}',f'k{ys}{p}',f'ord{yy}.{p}',f'off{y+37}.{n+7919}',f'tri{y*3+2}-{n*5+4}',f'win+{y-2010}/{n*3+1}',f'yr{y-1999}_n{n+17}',f'n{n+100000}_y{y-1900}',f'b36y{b36(y)}n{b36(n)}',f'h{y:x}x{n:x}',f'hexmix{n:x}_{y-1970}',f'b36mix{b36(y-1990)}_{p[::-1]}',f'rv{ys[::-1]}-{ns[::-1]}',f'z{b36(n+y)}.{ys[::-1]}',f'p{yy}{n%97:02d}.{cc}.{n}',f'fold{cc}{p[-2:]}-{yy}{p[:-2]}',f'sp{q[:2]}_{yy}_{q[2:]}_{cc}',f'mx{cc}-{q[:2]}-{yy}-{q[2:]}',f'swap{p[:3]}-{ys}-{p[3:]}',f'i{inter}','ri'+''.join(a+b for a,b in zip(ys[::-1],p[::-1][:4]))+p[::-1][4:]]
 # OCR forms allow independently substituted digits.
 fs += [f'ob{ys}-{ns}',f'ocrCVE{ys}{p}',f'ocrx{y+101}_{n+202}']
 # Dot encoding is the full year plus seven-digit sequence with arbitrary dots.
 fs += [f'dot{ys}{p}']
 return fs
lookup={}
for cid in ids:
 for f in forms(cid):lookup.setdefault(f,set()).add(cid)
# One inserted fragment consists of letters/digits and one punctuation character.
noise=re.compile(r'^(?:[A-P]{2}[!#$&]\d{3}|[A-P]{3}[!$]\d{2}|\d{3}[%?][A-P]{3}|\d{2}[%?][A-P]{2}[a-z0-9]|[A-P]{2}\d{2}[%?][A-P]|[A-P]{2}[~@][A-P]{3}|[~@][A-P]{2}[a-z0-9]{3}|[a-z0-9]{3}[&~#@][A-P]{2}|[a-z0-9]{3}[&#][A-P]{3}|[A-P][!$][a-z0-9]{3}[A-P])$')
ocr=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
def candidates(raw):
 # Remove source envelope while preserving the encoded payload.
 s=re.sub(r'^[a-z]+-[a-p]{5}(?:::ref=|::key=|::id=|::|=>|--|\+\+|~~|__|[~/#@%$|])','',raw)
 s=re.sub(r'^(?:(?:doc|key|slot|raw|join|ctx|id):)?[<({\[]?[a-p]{3}(?:::|[/:~|@#])?','',s)
 s=re.split(r':(?:doc|key|slot|raw|join|ctx|id)[a-p]{3}|[>)}\]][a-p]{3}(?=::|=>|--|\+\+|~~|__|[~/#@%$|])',s)[0]
 s=re.sub(r'[a-p]{3}(?:::|=>|--|\+\+|~~|__|[~/#@%$|])(?:aux=|end=|via=)?(?:src|slot|trace|tag|note|leaf|mark|batch|edge|frag|cache|trail|sink|node|tail|seen)-.*$','',s)
 yield s
 if re.match(r'^[A-P]{2}[a-z0-9]{3}',s):yield s[5:]
 for i in range(len(s)):
  for length in range(4,10):
   fragment=s[i:i+length]
   if len(fragment)==length and noise.fullmatch(fragment):yield s[:i]+s[i+length:]
def resolve(raw):
 found=set()
 for s in candidates(raw):
  if s.startswith(('ob','ocr')):s=s[:2]+s[2:].translate(ocr) if s.startswith('ob') else (('ocrCVE'+s[6:].translate(ocr)) if s.startswith('ocrCVE') else 'ocrx'+s[4:].translate(ocr))
  if s.startswith('dot'):s=s.replace('.','')
  found.update(lookup.get(s,()))
 return sorted(found)
if __name__=='__main__':
 rows=kev.select('cve_ref','cid').to_pyarrow().to_pylist()
 bad=[r for r in rows if r['cid'] not in resolve(r['cve_ref'])]
 print('KEV decoder validation',len(rows)-len(bad),'/',len(rows))
 assert not bad, 'Identifier decoder failed KEV validation'
 assert all(resolve(r['cve_ref']) == [r['cid']] for r in rows), 'Ambiguous KEV decoding'

 # Apply the scalar decoder inside DuckDB; all row filtering, vendor resolution,
 # date handling, joins, deduplication, and aggregation remain lazy Ibis work.
 @ibis.udf.scalar.python
 def decode_candidates(value: str) -> list[str]:
  return resolve(value)
 cves=table('vulns_db/cves.parquet')
 cves=cves.filter(cves.published.cast('timestamp').year()==2023)
 cves=cves.mutate(cid=decode_candidates(cves.cve_id).unnest())
 matches=table('cpe_db/cpe_matches.parquet')
 aliases=table('cpe_db/vendor_aliases.parquet')
 matches=matches.filter(matches.vulnerable_flag.strip().lower().isin(['1','yes','v','t','affected','true','y','vulnerable']))
 matches=matches.mutate(vendor=matches.criteria.re_extract(r'^(?:cpe:2\.3:[aho]:)?([^:/ ]+)',1))
 matches=matches.join(aliases,matches.vendor==aliases['alias']).filter(aliases.canonical_vendor=='apache')
 matches=matches.mutate(cid=decode_candidates(matches.cve_id).unnest())
 result=cves.select('cid').distinct().semi_join(matches.select('cid').distinct(),'cid').semi_join(kev.select('cid').distinct(),'cid')
 count=int(result.count().execute())
 (OUT/'matched_cves.json').write_text(json.dumps(result.order_by('cid').to_pyarrow().to_pylist(),indent=2))
 (OUT/'answer.json').write_text(json.dumps({'answer':str(count)}))
 print('Answer:',count)
 print(result.order_by('cid').to_pyarrow().to_pylist())
