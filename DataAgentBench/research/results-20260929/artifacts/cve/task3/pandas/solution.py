import re,json
import pandas as pd
# Remove complete noise tokens before extracting the encoded identifier.
NOISE_PATTERNS=[r'\d{2}[?%][A-P]{2}[a-z0-9]',r'[A-P]{2}\d{2}[?%][A-P]',r'[A-P]{3}[!$]\d{2}',r'[A-P]{2}[!#$&]\d{3}',r'[A-P]{2}[~@][A-P]{3}',r'[A-P][!$][a-z0-9]{3}[A-P]',r'\d{3}[?%&][A-P]{3}',r'\d{3}[~#&][A-P]{2}',r'[~@][A-P]{2}[a-z0-9]{3}',r'[a-z0-9]{3}[#&~@][A-P]{2,3}']
def clean(s):
 return s
def parse(s):
 s=clean(s)
 patterns=[
 (r'b36y([0-9a-z]{3})n([0-9a-z]+)',lambda a,b:(int(a,36),int(b,36))),
 (r'b36mix([0-9a-z]+)_([0-9]+)',lambda a,b:(int(a,36)+1990,int(b[::-1]))),
 (r'hexmix([0-9a-f]+)_([0-9a-f]+)',lambda a,b:(int(b)+1970,int(a,16))),
 (r'h([0-9a-f]+)x([0-9a-f]+)',lambda a,b:(int(a,16),int(b,16))),
 (r'ocrCVE([0-9OZISBG]{11})',lambda a:(int(a[:4].translate(OCR)),int(a[4:].translate(OCR)))),
 (r'ocrx([0-9OZISBG]{4})_([0-9OZISBG]+)',lambda a,b:(int(a.translate(OCR))-101,int(b.translate(OCR))-202)),
 (r'ob([0-9OZISBG]{4})-([0-9OZISBG]+)',lambda a,b:(int(a.translate(OCR)),int(b.translate(OCR)))),
 (r'fold(\d{4})-(\d+)',lambda a,b:(int(b[:2])+2000,int(b[2:]+a[2:]))),
 (r'swap(\d+)-(\d{4})-(\d+)',lambda a,b,c:(int(b),int(a+c))),
 (r'off(\d{4})\.(\d+)',lambda a,b:(int(a)-37,int(b)-7919)),
 (r'win\+(\d+)/(\d+)',lambda a,b:(2010+int(a),(int(b)-1)//3)),
 (r'tri(\d+)-(\d+)',lambda a,b:((int(a)-2)//3,(int(b)-4)//5)),
 (r'n(\d+)_y(\d+)',lambda a,b:(int(b)+1900,int(a)-100000)),
 (r'yr(\d+)_n(\d+)',lambda a,b:(int(a)+1999,int(b)-17)),
 (r'ord(\d+)\.(\d+)',lambda a,b:(int(a)+2000,int(b))),
 (r'rv(\d{4})-(\d+)',lambda a,b:(int(a[::-1]),int(b[::-1]))),
 (r'z([0-9a-z]+)\.(\d{4})',lambda a,b:(int(b[::-1]),int(a,36)-int(b[::-1]))),
 (r'mx(\d+)-(\d+)-(\d+)-(\d+)',lambda a,b,c,d:(int(a+c),int(b+d))),
 (r'sp(\d+)_(\d+)_(\d+)_(\d+)',lambda a,b,c,d:(int(d+b),int(a+c))),
 (r'p(\d{2})(\d{2})\.(\d{2})\.(\d+)',lambda a,b,c,d:(int(c+a),int(d))),
 (r'dot([\d.]+)',lambda a:(int(a.replace('.','')[:4]),int(a.replace('.','')[4:]))),
 (r'ri(\d{11})',lambda a:(int(a[0:8:2][::-1]),int((a[1:8:2]+a[8:])[::-1]))),
 (r'i(\d{11})',lambda a:(int(a[0:8:2]),int(a[1:8:2]+a[8:]))),
 (r'k(\d{4})(\d{7})',lambda a,b:(int(a),int(b))),
 (r'(?:CVE[-_]|cve[-:])?(20\d{2})[-_:]+(\d+)',lambda a,b:(int(a),int(b))),
 ]
 for pat,fn in patterns:
  m=re.search(pat,s)
  if m:
   if re.search(r'[A-Z0-9]',s[m.end():]): return None
   if re.search(r'[A-Z0-9]',s[:m.start()]): return None
   try: y,n=fn(*m.groups())
   except ValueError: return None
   return f'CVE-{y}-{n:04d}' if 1980<=y<=2027 and 0<n<10000000 else None
 return None
OCR=str.maketrans('OZISBG','021586')
def decode(s):
 candidates=set()
 for pat in NOISE_PATTERNS:
  # The last template can have a two- or three-letter noise suffix.
  for p in ([pat.replace('{2,3}','{2}'),pat.replace('{2,3}','{3}')] if '{2,3}' in pat else [pat]):
   for m in re.finditer(p,s):
    t=s[:m.start()]+s[m.end():]
    for u in [t,re.sub(r'[a-p]{3}(?=::|[|$@~%/]|--|\+\+|__|#|=>)', '', t)]:
     v=parse(u)
     if v: candidates.add(v)
 return '|'.join(sorted(candidates)) if candidates else None
if __name__=='__main__':
 nvd=pd.read_parquet('/workspace/data/vulns_db/cves.parquet',columns=['cve_id'])
 kev=pd.read_parquet('/workspace/data/kev_db/kev_entries.parquet',columns=['cve_ref','notes'])
 nvd['candidates']=nvd.cve_id.map(decode).str.split('|')
 kev['candidates']=kev.cve_ref.map(decode).str.split('|')
 # The catalog's explicit NVD detail links independently identify every KEV row.
 kev['key']=kev.notes.str.extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d+-\d+)')[0]
 assert kev.key.notna().all()
 assert all(k in c for k,c in zip(kev.key,kev.candidates))
 assert nvd.candidates.notna().all()
 single_mask=nvd.candidates.map(len).eq(1)
 certain=set(nvd.loc[single_mask,'candidates'].explode())
 possible=set(nvd.candidates.explode())
 # Only ambiguous NVD identifiers that can change the anti-join need resolution.
 decisive=set(kev.key)&(possible-certain)
 resolutions=[]
 for key in sorted(decisive):
  supported=False
  for idx in nvd.index[nvd.candidates.map(lambda c:key in c)]:
   previous=nvd.loc[:idx-1].loc[single_mask,'candidates'].iloc[-1][0]
   following=nvd.loc[idx+1:].loc[single_mask,'candidates'].iloc[0][0]
   def parts(k):
    _,y,n=k.split('-');return int(y),int(n)
   py,pn=parts(previous);fy,fn=parts(following)
   # Resolve only when both adjacent records bracket exactly one candidate
   # in the same year's ordered CVE run; never assume the whole table is sorted.
   bracketed=[c for c in nvd.at[idx,'candidates'] if parts(c)[0]==py==fy and pn<parts(c)[1]<fn]
   if bracketed==[key]:
    certain.add(key);supported=True
    resolutions.append({'raw':nvd.at[idx,'cve_id'],'resolved':key,'previous':previous,'following':following})
  assert supported, f'Unresolved match affecting the answer: {key}'
 missing=~kev.key.isin(certain)
 count=int(missing.sum())
 kev.assign(missing_nvd=missing).to_csv('/workspace/work/kev_audit.csv',index=False)
 with open('/workspace/work/normalization_audit.json','w') as f:
  json.dump({'nvd_rows':len(nvd),'kev_rows':len(kev),'decisive_resolutions':resolutions,'missing_entries':count},f,indent=2)
 with open('/workspace/work/answer.json','w') as f:
  json.dump({'answer':str(count)},f)
 print(count)
