import json,re
from pathlib import Path
import polars as pl
R=Path('/workspace/data'); W=Path('/workspace/work')
k=pl.read_parquet(R/'kev_db/kev_entries.parquet').filter(pl.col('known_ransomware_use')=='Known').join(pl.read_parquet(R/'kev_db/kev_vendor_aliases.parquet'),on='vendor_project').with_columns(pl.col('notes').str.extract(r'https://nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)',1).alias('cve')).select('canonical_vendor','cve').unique()
assert k['cve'].null_count()==0
s=pl.read_parquet(R/'vulns_db/cvss_metadata.parquet').with_columns(pl.col('score_text').str.extract(r'(\d+(?:\.\d+)?)',1).cast(pl.Float64).alias('score'))
def b36(v):
 out=''
 while v:v,r=divmod(v,36);out='0123456789abcdefghijklmnopqrstuvwxyz'[r]+out
 return out or '0'
# Construct the reversible identifier encodings, then use a trie to match
# them after removal of a single punctuation-bearing infix noise fragment.
trie={}
trans=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
all_ids=pl.read_parquet(R/'kev_db/kev_entries.parquet').select(pl.col('notes').str.extract(r'https://nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)',1).alias('cve')).drop_nulls()
for cve in all_ids['cve']:
 _,year,num=cve.split('-');y,n=int(year),int(num); pad=f'{n:07d}';digits=year+pad
 inter=''.join(a+b for a,b in zip(year,pad[:4]))+pad[4:]
 forms=[f'{prefix}{year}{sep}{number}' for sep in ['-','_',':','::'] for prefix in ['', 'CVE'+sep,'cve'+sep] for number in {num,pad}]
 forms += [f'off{y+37}.{n+7919}',f'win+{y-2010}/{3*n+1}',f'tri{3*y+2}-{5*n+4}',f'yr{y-1999}_n{n+17}',f'n{n+100000}_y{y-1900}',f'ord{y-2000}.{pad}',f'rv{year[::-1]}-{num[::-1]}',f'h{y:x}x{n:x}',f'b36y{b36(y)}n{b36(n)}',f'b36mix{b36(y-1990)}_{pad[::-1]}',f'hexmix{n:x}_{y-1970}',f'k{digits}',f'i{inter}',f"ri{''.join(a+b for a,b in zip(year[::-1],pad[::-1][:4]))+pad[::-1][4:]}",f'z{b36(n+y)}.{year[::-1]}',f'swap{pad[:3]}-{year}-{pad[3:]}',f'sp{num[:2]}_{year[2:]}_{num[2:]}_{year[:2]}',f'mx{year[:2]}-{num[:2]}-{year[2:]}-{num[2:]}',f'fold{year[:2]}{pad[-2:]}-{year[2:]}{pad[:-2]}',f'p{year[2:]}{n%97:02d}.{year[:2]}.{n}',f'ocrCVE{digits}',f'ob{year}-{num}',f'ocrx{y+101}_{n+202}']
 for form in forms:
  node=trie
  for char in form.translate(trans):node=node.setdefault(char,{})
  node.setdefault('',set()).add(cve)
noise=re.compile(r'^(?:[0-9]{2}[!@#$%&?~][A-P]{2}[a-z0-9]|[A-P]{2}[0-9]{2}[!@#$%&?~][A-P]|[A-P]{2}[!@#$%&?~][0-9]{3}|[A-P]{3}[!@#$%&?~][0-9]{2}|[0-9]{3}[!@#$%&?~][A-P]{2,3}|[a-z0-9]{3}[!@#$%&?~][A-P]{2,3}|[A-P]{2}[!@#$%&?~][A-P]{3}|[A-P][!@#$%&?~][a-z0-9]{3}[A-P]|[!@#$%&?~][A-P]{2}[a-z0-9]{3})$')
def candidates(raw):
 yield raw
 for i in range(len(raw)):
  for size in range(3,10):
   frag=raw[i:i+size]
   if noise.fullmatch(frag) and any(c in '!@#$%&?~' for c in frag) and any('A'<=c<='P' for c in frag):
    yield raw[:i]+raw[i+size:]
def match(raw):
 found=set()
 for clean in candidates(raw):
  clean=clean.translate(trans)
  # Dot encoding splits the packed numeric identifier at arbitrary positions.
  clean=re.sub(r'dot([\d.]+)',lambda m:'k'+m[1].replace('.',''),clean)
  for i,ch in enumerate(clean):
   if ch not in trie:continue
   node=trie; j=i
   while j<len(clean) and clean[j] in node:
    node=node[clean[j]];j+=1
    if '' in node and (j==len(clean) or not clean[j].isalnum() or re.match(r'[a-p]{3}[^a-zA-Z0-9]',clean[j:])):found.update(node[''])
 return sorted(found)
# Verify identifier recovery against KEV rows whose notes supply independent IDs.
check=pl.read_parquet(R/'kev_db/kev_entries.parquet').with_columns(pl.col('notes').str.extract(r'https://nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)',1).alias('expected'))
failures=[{'raw':row['cve_ref'],'expected':row['expected'],'got':match(row['cve_ref'])} for row in check.iter_rows(named=True) if row['expected'] not in match(row['cve_ref'])]
(W/'decode_failures.json').write_text(json.dumps(failures,indent=2))
print('Identifier recovery failures:',len(failures),flush=True)
docs=pl.read_parquet(R/'descriptions_db/cve_documents.parquet').rename({'cve':'raw_cve'}).with_columns(pl.col('raw_cve').map_elements(match,return_dtype=pl.List(pl.String)).alias('cve')).explode('cve').filter(pl.col('cve').is_not_null())
def english(text):
 return ' '.join(d['value'] for d in json.loads(text or '[]') if d.get('lang')=='en')
# Severity is encoded in English description taglines or equivalent narrative.
docs=docs.with_columns(pl.col('descriptions').map_elements(english,return_dtype=pl.String).alias('english'))
critical_pattern=r'(?i)(risk-level: 4-of-4|threat tier: T4|impact band: red-zone|fully take over|complete(?:ly)? (?:loss|control|takeover|take over)|total (?:loss|compromise)|trivially weaponized|unrestricted control over the system)'
critical=docs.filter(pl.col('english').str.contains(critical_pattern)).select('cve').unique()
counts=k.group_by('canonical_vendor').agg(pl.len().alias('total')).filter(pl.col('total')>=3)
r=k.join(critical,on='cve').group_by('canonical_vendor').agg(pl.len().alias('critical')).join(counts,on='canonical_vendor').sort('critical',descending=True)
print(r)
assert r['critical'][0]>r['critical'][1]
r.write_csv(W/'vendor_counts.csv')
docs.join(k,on='cve').write_parquet(W/'severity_evidence.parquet')
(W/'answer.json').write_text(json.dumps({'answer':r['canonical_vendor'][0]}))
