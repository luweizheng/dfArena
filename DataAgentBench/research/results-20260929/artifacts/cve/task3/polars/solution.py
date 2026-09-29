import re,json
from pathlib import Path
import polars as pl
SYM=r'[!@#$%&?~]'
noise=re.compile('|'.join([r'[A-P]{2}\d{2}'+SYM+r'[A-P]',r'\d{3}'+SYM+r'[A-P]{2,3}',r'\d{2}'+SYM+r'[A-P]{2}[a-z0-9]',r'[A-P]{3}'+SYM+r'\d{2}',r'[A-P]{2}'+SYM+r'\d{3}',r'[A-P]{2}'+SYM+r'[A-P]{3}',r'[A-P]'+SYM+r'[a-z0-9]{3}[A-P]',r'[@~][A-P]{2}[a-z0-9]{3}',r'[a-z0-9]{3}'+SYM+r'[A-P]{2}',r'[a-z0-9]{3}'+SYM+r'[A-P]{3}']))
def clean(s): return noise.sub('',s)
# Decode each recoverable representation after removing the inserted fragment.
ocr=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
def decode_payload(s):
 specs=[
 (r'(?:CVE[-_:]|cve[-_:])?(\d{4})[-_:]{1,2}(\d{1,8})',lambda a,b:(int(a),int(b))),
 (r'k(\d{4})(\d{7})',lambda a,b:(int(a),int(b))),
 (r'ord(\d{2})\.(\d{7})',lambda a,b:(2000+int(a),int(b))),
 (r'off(\d{4})\.(\d+)',lambda a,b:(int(a)-37,int(b)-7919)),
 (r'yr(\d+)_n(\d+)',lambda a,b:(2000+int(a)-1,int(b)-17)),
 (r'n(\d+)_y(\d+)',lambda a,b:(1900+int(b),int(a)-100000)),
 (r'win\+(\d+)/(\d+)',lambda a,b:(2010+int(a),(int(b)-1)//3)),
 (r'tri(\d+)-(\d+)',lambda a,b:((int(a)-2)//3,(int(b)-4)//5)),
 (r'rv(\d{4})-(\d+)',lambda a,b:(int(a[::-1]),int(b[::-1]))),
 (r'z([a-z0-9]+)\.(\d{4})',lambda a,b:(int(b[::-1]),int(a,36)-int(b[::-1]))),
 (r'h([a-f0-9]+)x([a-f0-9]+)',lambda a,b:(int(a,16),int(b,16))),
 (r'b36y([a-z0-9]{3})n([a-z0-9]+)',lambda a,b:(int(a,36),int(b,36))),
 (r'b36mix([a-z0-9]+)_(\d{7})',lambda a,b:(1990+int(a,36),int(b[::-1]))),
 (r'hexmix([a-f0-9]+)_([a-f0-9]+)',lambda a,b:(1970+int(b),int(a,16))),
 (r'mx(\d{2})-(\d+)-(\d{2})-(\d{1,4})',lambda a,b,c,d:(int(a+c),int(b+d))),
 (r'sp(\d+)_(\d{2})_(\d+)_(\d{2})',lambda a,b,c,d:(int(d+b),int(a+c))),
 (r'swap(\d+)-(\d{4})-(\d+)',lambda a,b,c:(int(b),int(a+c))),
 (r'p(\d{4})\.(\d{2})\.(\d+)',lambda a,b,c:(int(b+a[:2]),int(c))),
 (r'fold(\d{4})-(\d{7})',lambda a,b:(int(str(a)[:2]+b[:2]),int(b[2:]+a[2:]))),
 (r'ocrx([0-9OIZSGB]+)_([0-9OIZSGB]+)',lambda a,b:(int(a.translate(ocr))-101,int(b.translate(ocr))-202)),
 (r'ob([0-9OIZSGB]+)-([0-9OIZSGB]+)',lambda a,b:(int(a.translate(ocr)),int(b.translate(ocr)))),
 (r'ocrCVE([0-9OIZSGB]{4})([0-9OIZSGB]{7})',lambda a,b:(int(a.translate(ocr)),int(b.translate(ocr)))),
 (r'dot([0-9.]+)',lambda a: (int(a.replace('.','')[:4]),int(a.replace('.','')[4:]))),
 (r'ri(\d{11})',lambda a:(int(a[:8:2][::-1]),int((a[1:8:2]+a[8:])[::-1]))),
 (r'i(\d{11})',lambda a:(int(a[:8:2]),int(a[1:8:2]+a[8:]))),
 ]
 out=set()
 for pat,fn in specs:
  for m in re.finditer(pat+r'(?=(?::(?:id|doc|raw|slot|key|join|ctx)[a-p]{3}|[\]\)}>])|[a-p]{3}(?:[~@#$%/|>:=_+-]|--|__|\+\+))',s):
   # Payload must be followed by a wrapper delimiter or the three-letter wrapper suffix.
   head=s[:m.start()]
   if re.search(r'[0-9A-Z]',head): continue
   if not re.search(r'(?:[:~@/#|><\[({$%_+=-]|[:~@/#|><\[({$%_+=-][a-p]{3})$',head): continue
   tail=s[m.end():]
   if re.search(r'[0-9A-Z]',tail): continue
   if not re.match(r'(?:(?::(?:id|doc|raw|slot|key|join|ctx)[a-p]{3}|[\]\)}>])|[a-p]{3}(?:[~@#$%/|>:=_+-]|--|__|\+\+))',tail): continue
   try:
    y,n=fn(*m.groups())
    if 1990<=y<=2030 and 0<=n<10000000: out.add(f'CVE-{y}-{n:04d}')
   except ValueError: pass
 return out
patterns=[re.compile(p) for p in noise.pattern.split('|')]
def candidates(s):
 out=set()
 scored=[]
 for pat in patterns:
  for m in pat.finditer(s):
   decoded=decode_payload(s[:m.start()]+s[m.end():])
   if decoded: scored.append((freq.get(m.group(),0),len(m.group()),decoded))
 if not scored:return []
 best=max((x[0],x[1]) for x in scored)
 for count,length,decoded in scored:
  if (count,length)==best:out.update(decoded)
 return sorted(out)
if __name__=='__main__':
 from collections import Counter
 frames=[pl.read_parquet('/workspace/data/'+t+'.parquet').select(c) for t,c in [('vulns_db/cves','cve_id'),('kev_db/kev_entries','cve_ref')]]
 freq=Counter()
 for d in frames:
  for s in d.to_series():
   for token in set(m.group() for pat in patterns for m in pat.finditer(s)):freq[token]+=1
 for d,name in zip(frames,['cves','kev_entries']):
  d=d.with_columns(pl.col(d.columns[0]).map_elements(candidates,return_dtype=pl.List(pl.String)).alias('candidates'))
  d.write_parquet('/workspace/work/'+name+'_decoded.parquet')
  print(name,d.group_by(pl.col('candidates').list.len()).len())
  print(d.filter(pl.col('candidates').list.len()!=1).head(30).to_dicts())
 # Independently verify KEV decoding against its catalog reference URLs.
 kev_full=pl.read_parquet('/workspace/data/kev_db/kev_entries.parquet')
 kev=pl.read_parquet('/workspace/work/kev_entries_decoded.parquet')
 refs=kev_full.select('cve_ref',pl.col('notes').str.extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)').alias('canonical'))
 checked=kev.join(refs,on='cve_ref')
 assert checked.filter(~pl.col('candidates').list.contains(pl.col('canonical'))).height==0
 assert checked['canonical'].null_count()==0
 nvd=pl.read_parquet('/workspace/work/cves_decoded.parquet')
 assert nvd.filter(pl.col('candidates').list.len()==0).height==0
 # Any unresolved alternatives must give identical membership for KEV IDs.
 kev_ids=set(checked['canonical'])
 for row in nvd.filter(pl.col('candidates').list.len()>1).iter_rows(named=True):
  assert not (set(row['candidates']) & kev_ids)
 unmatched=checked.join(nvd.select(pl.col('candidates').explode().alias('canonical')).unique(),on='canonical',how='anti')
 unmatched.select('cve_ref','canonical').write_csv('/workspace/work/unmatched_kev.csv')
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(unmatched.height)}))
 print('Unmatched KEV entries:',unmatched.height)
 # Check all structurally valid alternatives, without frequency selection.
 possible=set()
 for s in frames[0].to_series():
  for pat in patterns:
   for m in pat.finditer(s): possible.update(decode_payload(s[:m.start()]+s[m.end():]))
 extra=(possible & kev_ids)-set(nvd['candidates'].explode())
 print('Additional KEV matches under any alternative:',sorted(extra))
 assert not extra
