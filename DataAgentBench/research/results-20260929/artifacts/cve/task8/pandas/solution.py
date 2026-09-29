import pandas as pd, re, json
from pathlib import Path
ROOT=Path('/workspace/data')
def read(p):return pd.read_parquet(ROOT / (p+'.parquet'))
# Keep all possible noise boundaries; the KEV identifier set resolves ambiguity.
noise_patterns=[r'[A-P]{2}\d{2}[%?][A-P]',r'[A-P]{2}[@~][A-P]{3}',r'[@~][A-P]{2}[a-z0-9]{3}',r'[A-P][!$][a-z0-9]{3}[A-P]',r'[A-P]{3}[!$]\d{2}',r'[A-P]{2}[!$&#]\d{3}',r'[a-z0-9]{3}[#&@~%?][A-P]{2}',r'[a-z0-9]{3}[#&@~%?][A-P]{3}',r'\d{2}[%?][A-P]{2}[a-z0-9]']
noises=[re.compile('(?=('+p+'))') for p in noise_patterns]
def variants(s):
 for pat in noises:
  for m in pat.finditer(s):yield s[:m.start()]+s[m.start()+len(m[1]):]
ocr=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
rules=[]
def rule(p,f):rules.append((re.compile(p),f))
rule(r'(?:CVE[-_:]|cve[-:])?(\d{4})[-_:]{1,2}(\d{4,7})',lambda a,b:(int(a),int(b)))
rule(r'ocrCVE([0-9OIZSGB]{11})',lambda a:(int(a.translate(ocr)[:4]),int(a.translate(ocr)[4:])))
rule(r'ob([0-9OIZSGB]{4})-([0-9OIZSGB]+)',lambda a,b:(int(a.translate(ocr)),int(b.translate(ocr))))
rule(r'ocrx([0-9OIZSGB]{4})_([0-9OIZSGB]+)',lambda a,b:(int(a.translate(ocr))-101,int(b.translate(ocr))-202))
rule(r'rv(\d{4})-(\d+)',lambda a,b:(int(a[::-1]),int(b[::-1])))
rule(r'off(\d{4})\.(\d+)',lambda a,b:(int(a)-37,int(b)-7919))
rule(r'tri(\d+)-(\d+)',lambda a,b:((int(a)-2)//3,(int(b)-4)//5) if (int(a)-2)%3==0 and (int(b)-4)%5==0 else (0,0))
rule(r'win\+(\d+)/(\d+)',lambda a,b:(int(a)+2010,(int(b)-1)//3) if (int(b)-1)%3==0 else (0,0))
rule(r'yr(\d+)_n(\d+)',lambda a,b:(int(a)+1999,int(b)-17))
rule(r'n(\d+)_y(\d+)',lambda a,b:(int(b)+1900,int(a)-100000))
rule(r'ord(\d+)\.(\d+)',lambda a,b:(int(a)+2000,int(b)))
rule(r'h([0-9a-f]+)x([0-9a-f]+)',lambda a,b:(int(a,16),int(b,16)))
rule(r'b36y([0-9a-z]{3})n([0-9a-z]+)',lambda a,b:(int(a,36),int(b,36)))
rule(r'b36mix([0-9a-z]+)_(\d+)',lambda a,b:(int(a,36)+1990,int(b[::-1])))
rule(r'hexmix([0-9a-f]+)_([0-9a-f]+)',lambda a,b:(int(b)+1970,int(a,16)))
rule(r'z([0-9a-z]+)\.(\d{4})',lambda a,b:(int(b[::-1]),int(a,36)-int(b[::-1])))
rule(r'p(\d{2})\d{2}\.(\d{2})\.(\d+)',lambda a,b,c:(int(b+a),int(c)))
rule(r'fold(\d{4})-(\d{7})',lambda a,b:(int(a[:2]+b[:2]),int(b[2:]+a[2:])))
rule(r'swap(\d{3})-(\d{4})-(\d{4})',lambda a,b,c:(int(b),int(a+c)))
rule(r'sp(\d+)_(\d{2})_(\d+)_(\d{2})',lambda a,b,c,d:(int(d+b),int(a+c)))
rule(r'mx(\d{2})-(\d+)-(\d{2})-(\d+)',lambda a,b,c,d:(int(a+c),int(b+d)))
rule(r'k(\d{11})',lambda a:(int(a[:4]),int(a[4:])))
def inter(a):return int(a[0:8:2]),int(a[1:8:2]+a[8:])
rule(r'i(\d{11})',inter)
rule(r'ri(\d{11})',lambda a:(int(a[0:8:2][::-1]),int((a[1:8:2]+a[8:])[::-1])))
rule(r'dot([\d.]+)',lambda a:(int(a.replace('.','')[:4]),int(a.replace('.','')[4:])))

def candidates(s,allowed):
 out=set()
 for v0 in variants(s):
  for v in [v0]+[v0[:i] for i in range(max(0,len(v0)-45),len(v0)) if re.match(r"[a-p]{3}(?=[^a-z0-9]|$)",v0[i:])]:
   for pat,fn in rules:
    for m in re.finditer('(?=('+pat.pattern+'))',v):
     tail=v[m.start()+len(m[1]):]
     if tail and tail[0].isalnum() and not re.match(r"[a-p]{3}(?=[^a-z0-9]|$)",tail):continue
     try:
      y,n=fn(*m.groups()[1:]); key=f'CVE-{y:04d}-{n:04d}'
      if key in allowed:out.add(key)
     except ValueError:pass
 return out

if __name__=='__main__':
 k=read('kev_db/kev_entries')
 k['canonical']=k.notes.str.extract(r'nvd.nist.gov/vuln/detail/(CVE-\d{4}-\d+)')
 assert k.canonical.notna().all()
 allowed=set(k.canonical)
 failed=[]
 for row in k.itertuples():
  cs=candidates(row.cve_ref,allowed)
  if cs != {row.canonical}:failed.append((row.canonical,row.cve_ref,sorted(cs)))
 assert not failed, failed
 print('Validated all KEV identifier encodings',flush=True)
 c=read('cpe_db/cpe_matches'); aliases=read('cpe_db/vendor_aliases')
 c['alias']=c.criteria.str.extract(r'^cpe:2\.3:[^:]+:([^:]+):')[0].fillna(c.criteria.str.extract(r'^([^/\s]+)')[0])
 c=c.merge(aliases,on='alias',how='left',validate='many_to_one')
 assert c.canonical_vendor.notna().all()
 truth={'t','y','yes','affected','vulnerable','v','true','1'}
 ms=c.loc[c.canonical_vendor.eq('microsoft') & c.vulnerable_flag.str.strip().str.lower().isin(truth),'cve_id'].drop_duplicates()
 msmap={s:candidates(s,allowed) for s in ms}
 assert all(len(v)<=1 for v in msmap.values())
 msids=set().union(*msmap.values())
 Path('/workspace/work/ms_matches.json').write_text(json.dumps({x:sorted(y) for x,y in msmap.items() if y},indent=2))
 print('Microsoft KEV IDs',len(msids), 'ambiguous',sum(len(x)>1 for x in msmap.values()),flush=True)
 scores=read('vulns_db/cvss_metadata')
 scores['score']=pd.to_numeric(scores.score_text.str.extract(r'(\d+(?:\.\d+)?)')[0],errors='raise')
 high=scores.loc[scores.score.ge(7),'cve_id'].drop_duplicates()
 smap={s:candidates(s,msids) for s in high}
 assert all(len(v)<=1 for v in smap.values())
 result=sorted(set().union(*smap.values()))
 Path('/workspace/work/score_matches.json').write_text(json.dumps({x:sorted(y) for x,y in smap.items() if y},indent=2))
 print('High-score ambiguous',sum(len(x)>1 for x in smap.values()),'answer',len(result),flush=True)
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(len(result))}))
 pd.DataFrame({'cve_id':result}).to_csv('/workspace/work/matching_cves.csv',index=False)
