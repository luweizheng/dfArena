import re,json
from pathlib import Path
import polars as pl
NOISE_PATTERNS=[
 r'[A-P]{2}\d{2}[%?][A-P]',
 r'[A-P]{3}[!$]\d{2}',r'[A-P]{2}[@~][A-P]{3}',r'[A-P][!$][a-z0-9]{3}[A-P]',
 r'[A-P]{2}[!#$&]\d{3}',r'[@~][A-P]{2}[a-z0-9]{3}',
 r'\d{3}[%?][A-P]{3}',r'\d{2}[%?][A-P]{2}[a-z0-9]',
 r'[a-z0-9]{3}[#&][A-P]{3}',r'[a-z0-9]{3}[@~#&][A-P]{2}',
]
def clean(s):
 return re.sub('|'.join(NOISE_PATTERNS), '', s)
OCR=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
def decode_clean(s):
 patterns=[
 ('b36y',r'b36y([a-z0-9]{3})n([a-z0-9]+)'),
 ('b36mix',r'b36mix([a-z0-9]+)_(\d+)'),
 ('hexmix',r'hexmix([a-f0-9]+)_([a-f0-9]+)'),
 ('h',r'h([a-f0-9]+)x([a-f0-9]+)'),
 ('off',r'off(\d+)\.(\d+)'),
 ('yr',r'yr(\d+)_n(\d+)'),
 ('n',r'n(\d+)_y(\d+)'),
 ('ord',r'ord(\d{2})\.(\d+)'),
 ('tri',r'tri(\d+)-(\d+)'),
 ('win',r'win\+(\d+)/(\d+)'),
 ('swap',r'swap(\d+)-(\d{4})-(\d+)'),
 ('mx',r'mx(\d{2})-(\d+)-(\d{2})-(\d+)'),
 ('sp',r'sp(\d+)_(\d{2})_(\d+)_(\d{2})'),
 ('fold',r'fold(\d{4})-(\d+)'),
 ('p',r'p(\d{4})\.(\d{2})\.(\d+)'),
 ('rv',r'rv(\d{4})-(\d+)'),
 ('z',r'z([a-z0-9]+)\.(\d{4})'),
 ('ocrx',r'ocrx([0-9OIZSGB]{4})_([0-9OIZSGB]+)'),
 ('ocrCVE',r'ocrCVE([0-9OIZSGB]{11})'),
 ('ob',r'ob([0-9OIZSGB]{4})-([0-9OIZSGB]+)'),
 ('k',r'k(\d{11})'),('ri',r'ri(\d{11})'),('i',r'i(\d{11})'),
 ('dot',r'dot([\d.]+)'),
 ('plain',r'(?:CVE[-_:]|cve[-_:])?((?:19|20)\d{2})[-_:]+(\d+)'),
 ]
 for kind,pat in patterns:
  m=re.search(pat,s)
  if not m:continue
  # All numeric and uppercase content belongs to the encoded payload.
  outside=s[:m.start()]+s[m.end():]
  if re.search(r'[0-9A-Z]|swap',outside):continue
  a=m.groups()
  try:
   if kind=='b36y': y,n=map(lambda x:int(x,36),a)
   elif kind=='b36mix': y,n=1990+int(a[0],36),int(a[1][::-1])
   elif kind=='hexmix': y,n=1970+int(a[1]),int(a[0],16)
   elif kind=='h': y,n=int(a[0],16),int(a[1],16)
   elif kind=='off': y,n=int(a[0])-37,int(a[1])-7919
   elif kind=='yr': y,n=int(a[0])+1999,int(a[1])-17
   elif kind=='n': y,n=int(a[1])+1900,int(a[0])-100000
   elif kind=='ord': y,n=int(a[0])+2000,int(a[1])
   elif kind=='tri': y,n=(int(a[0])-2)//3,(int(a[1])-4)//5
   elif kind=='win': y,n=int(a[0])+2010,(int(a[1])-1)//3
   elif kind=='swap': y,n=int(a[1]),int(a[0]+a[2])
   elif kind=='mx': y,n=int(a[0]+a[2]),int(a[1]+a[3])
   elif kind=='sp': y,n=int(a[3]+a[1]),int(a[0]+a[2])
   elif kind=='fold': y,n=int(a[0][:2]+a[1][:2]),int(a[1][2:]+a[0][2:])
   elif kind=='p': y,n=int(a[1]+a[0][:2]),int(a[2])
   elif kind=='rv': y,n=int(a[0][::-1]),int(a[1][::-1])
   elif kind=='z': y,n=int(a[1][::-1]),int(a[0],36)-int(a[1][::-1])
   elif kind in ('ocrx','ob'): y,n=int(a[0].translate(OCR)),int(a[1].translate(OCR)); y-=101 if kind=='ocrx' else 0; n-=202 if kind=='ocrx' else 0
   elif kind in ('ocrCVE','k','dot'):
    v=a[0].translate(OCR).replace('.',''); y,n=int(v[:4]),int(v[4:])
   elif kind in ('ri','i'):
    v=a[0]; ys=v[:8:2]; ns=v[1:8:2]+v[8:]
    if kind=='ri':ys,ns=ys[::-1],ns[::-1]
    y,n=int(ys),int(ns)
   else:y,n=map(int,a)
   if not(1990<=y<=2030 and 0<n<2000000):continue
   return f'CVE-{y}-{n:04d}'
  except ValueError:continue
 return None

def decode(raw):
 candidates=[]
 for pat in NOISE_PATTERNS:
  for m in re.finditer(pat,raw):
   s=raw[:m.start()]+raw[m.end():]
   # Remaining uppercase characters must belong to CVE/OCR encodings.
   stripped=re.sub(r'CVE|[OIZSGB]', '', s)
   if re.search('[A-Z]',stripped):continue
   # Wrapper letters immediately following numeric base encodings are not payload.
   for candidate in [s,re.sub(r'([a-z0-9])[a-z]{3}(?=[:#~@%$|/]|__|--|=>|\+\+)',r'\1',s)]:
    ans=decode_clean(candidate)
    if ans and ans not in candidates:candidates.append(ans)
 return candidates

def main():
 outdir=Path('/workspace/work')
 v=pl.read_parquet('/workspace/data/vulns_db/cves.parquet').with_columns(
  pl.col('cve_id').map_elements(decode,return_dtype=pl.List(pl.String)).alias('candidates'))
 k=pl.read_parquet('/workspace/data/kev_db/kev_entries.parquet').with_columns(
  pl.col('cve_ref').map_elements(decode,return_dtype=pl.List(pl.String)).alias('candidates'),
  pl.col('notes').str.extract_all(r'nvd\.nist\.gov/vuln/detail/CVE-\d{4}-\d+').list.eval(
   pl.element().str.extract(r'(CVE-\d{4}-\d+)')).list.unique().alias('note_ids'))
 # The catalog's own NVD links independently disambiguate its noisy join keys.
 k=k.with_columns(pl.when(pl.col('note_ids').list.len()==1)
  .then(pl.col('candidates').list.set_intersection(pl.col('note_ids')))
  .otherwise(pl.col('candidates')).alias('candidates'))
 assert v['candidates'].list.len().min()>0
 assert k['candidates'].list.len().min()>0
 def matches(definite):
  vv=v.filter(pl.col('candidates').list.len()==1) if definite else v
  kk=k.filter(pl.col('candidates').list.len()==1) if definite else k
  return (vv.explode('candidates').group_by('candidates').agg(
   pl.len().alias('rows'),
   pl.col('cvss3_attack_vector').drop_nulls().n_unique().alias('vector_count'))
   .filter((pl.col('rows')>1)&(pl.col('vector_count')>1))
   .join(kk.explode('candidates').select('candidates').unique(),on='candidates',how='semi')
   .sort('candidates'))
 lower,upper=matches(True),matches(False)
 # Any remaining surface-form ambiguity cannot affect this question:
 # definite matches and the superset of all possible matches coincide.
 assert lower['candidates'].to_list()==upper['candidates'].to_list(), (lower,upper)
 lower.rename({'candidates':'cve'}).write_csv(outdir/'matching_cves.csv')
 (outdir/'answer.json').write_text(json.dumps({'answer':str(lower.height)}))
 print(json.dumps({'answer':str(lower.height)}))

if __name__=='__main__':
 main()
