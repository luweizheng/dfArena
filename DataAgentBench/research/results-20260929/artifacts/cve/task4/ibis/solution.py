import re,json,functools
from pathlib import Path
import ibis
ROOT=Path('/workspace/data'); OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
def table(p):return con.read_parquet(str(ROOT/(p+'.parquet')))
kev=table('kev_db/kev_entries')
# Catalog notes expose standard NVD identifiers and provide an independent
# dictionary for lossless decoding of the deliberately obscured join keys.
note_rows=kev.select('cve_ref','notes').to_pyarrow().to_pylist()
ids=set()
for r in note_rows:
 ids.update(x.upper() for x in re.findall(r'CVE-\d{4}-\d{4,}',r['notes'] or '',re.I))
def b36(n):
 s=''; chars='0123456789abcdefghijklmnopqrstuvwxyz'
 while n:s=chars[n%36]+s;n//=36
 return s or '0'
def variants(cve):
 _,ys,ns=cve.split('-'); y=int(ys);n=int(ns);p=f'{n:07d}'; yy=f'{y%100:02d}'
 v=[f'CVE-{ys}-{ns}',f'cve-{ys}-{ns}',f'CVE_{ys}_{ns}',f'cve:{ys}:{ns}',f'{ys}-{ns}',f'{ys}:{ns}',f'{ys}::{ns}',f'{ys}_{ns}',
 f'k{ys}{p}',f'yr{y-1999}_n{n+17}',f'n{n+100000}_y{y-1900}',f'off{y+37}.{n+7919}',f'win+{y-2010}/{n*3+1}',f'tri{y*3+2}-{n*5+4}',
 f'rv{ys[::-1]}-{ns[::-1]}',f'ord{yy}.{p}',f'h{y:x}x{n:x}',f'b36y{b36(y)}n{b36(n)}',f'hexmix{n:x}_{y-1970}',f'b36mix{b36(y-1990)}_{p[::-1]}',
 f'fold{2000+n%100}-{yy}{n//100:05d}',f'p{yy}{n%97:02d}.{ys[:2]}.{n}',f'swap{p[:3]}-{ys}-{p[3:]}',f'mx{ys[:2]}-{ns[:2]}-{yy}-{ns[2:]}',f'sp{ns[:2]}_{yy}_{ns[2:]}_{ys[:2]}']
 inter=''.join(a+b for a,b in zip(ys,p[:4]))+p[4:]
 rev=''.join(a+b for a,b in zip(ys[::-1],p[::-1][:4]))+p[::-1][4:]
 v += ['i'+inter,'ri'+rev, f'z{b36(n+y)}.{ys[::-1]}', 'dot'+ys+p]
 # Digit grouping in dot form is arbitrary.
 v += ['ocrCVE'+ys+p,'ob'+ys+'-'+ns,'ocrx'+str(y+101)+'_'+str(n+202)]
 return v
# Match a known encoded identifier while allowing a single inserted noise
# fragment (six or seven characters), including insertions inside a token.
noise_pattern=re.compile(r'(?:[A-P]{2}[!#$&][0-9]{3}|[A-P]{3}[!$][0-9]{2}|[0-9]{3}[%?][A-P]{3}|[A-P]{2}[0-9]{2}[%?][A-P]|[0-9]{2}[%?][A-P]{2}[a-z0-9]|[A-P]{2}[@~][A-P]{3}|[a-z0-9]{3}[@#~&][A-P]{2}|[a-z0-9]{3}[#&][A-P]{3}|[@~][A-P]{2}[a-z0-9]{3}|[A-P][!$][a-z0-9]{3}[A-P])')
trie={}
for cv in ids:
 for v in variants(cv):
  if v.startswith(('ocr','ob')):
   # OCR substitutions are normalized consistently in input and dictionary.
   v=v.translate(str.maketrans('OIZSBG','012586'))
  node=trie
  for ch in v:node=node.setdefault(ch,{})
  node.setdefault('',set()).add(cv)
@functools.lru_cache(maxsize=None)
def decode(raw):
 s=raw.translate(str.maketrans('OIZSBG','012586'))
 results=set()
 def walk(pos,node,skipped):
  while True:
   if s[start]=='d' and pos<len(s) and s[pos]=='.':pos+=1;continue
   if '' in node:
    # Prevent partial numeric matches.
    if pos==len(s) or not s[pos].isdigit():results.update((cv,pos-start-len(skipped),skipped) for cv in node[''])
   if pos>=len(s):return
   if not skipped:
    for length in (6,7):
     fragment=raw[pos:pos+length]
     if len(fragment)==length and noise_pattern.fullmatch(fragment):
      walk(pos+length,node,fragment)
   node=node.get(s[pos]);pos+=1
   if node is None:return
 for start,ch in enumerate(s):
  if ch in trie:walk(start,trie,'')
 
 return results

def resolve(raw):
 all_candidates=decode(raw)
 candidates={item for item in all_candidates if item[2]} or all_candidates
 if not candidates:return None
 best=max(score for cv,score,frag in candidates)
 winners={cv for cv,score,frag in candidates if score==best}
 return next(iter(winners)) if len(winners)==1 else None

if __name__=='__main__':
 bad=[]
 for r in note_rows:
  expected={x.upper() for x in re.findall(r'CVE-\d{4}-\d{4,}',r['notes'] or '',re.I)}
  got=resolve(r['cve_ref'])
  if got not in expected:bad.append((r['cve_ref'],got,expected))
 print('KEV decoding mismatches',len(bad));print(*bad[:20],sep='\n')

 assert not bad, bad
 @ibis.udf.scalar.python
 def canonical_cve(value: str) -> str:
  return resolve(value) or ''
 cpe=table('cpe_db/cpe_matches')
 scores=table('vulns_db/cvss_metadata')
 aliases=table('kev_db/kev_vendor_aliases')
 vulnerable=(cpe.filter(cpe.vulnerable_flag.strip().lower().isin(['true','t','1','yes','y','v','vulnerable','affected']))
   .select(cve=canonical_cve(cpe.cve_id)).filter(ibis._.cve != '').distinct())
 normalized_scores=scores.select(cve=canonical_cve(scores.cve_id),score=scores.score_text.re_extract(r'([0-9]+(?:\.[0-9]+)?)',1).cast('float64'))
 normalized_scores=normalized_scores.filter(ibis._.cve != '').group_by('cve').aggregate(score=ibis._.score.max())
 k=kev.select(cve=canonical_cve(kev.cve_ref),vendor_project=kev.vendor_project)
 vendor_cves=k.join(aliases,'vendor_project').select('cve',canonical_vendor=aliases.canonical_vendor.lower()).distinct()
 eligible=vendor_cves.semi_join(vulnerable,'cve').left_join(normalized_scores,'cve')
 ranked=(eligible.group_by('canonical_vendor').aggregate(total=ibis._.cve.nunique(),critical=ibis._.cve.nunique(where=(ibis._.score>=9).fill_null(False))))
 ranked=ranked.filter(ranked.total>=10).mutate(share=ibis._.critical/ibis._.total).order_by(ibis.desc('share'),'canonical_vendor')
 results=ranked.to_pyarrow().to_pylist()
 (OUT/'vendor_shares.json').write_text(json.dumps(results,indent=2))
 assert results
 (OUT/'answer.json').write_text(json.dumps({'answer':results[0]['canonical_vendor']}))
 print(json.dumps(results[:10],indent=2))
