import re,json
from pathlib import Path
import polars as pl
ROOT=Path('/workspace/data')
def read(p): return pl.read_parquet(ROOT/p)
# The KEV notes contain explicit canonical NVD links, independent of noisy keys.
kev=read('kev_db/kev_entries.parquet').join(read('kev_db/kev_vendor_aliases.parquet'),on='vendor_project',validate='m:1').filter(pl.col('canonical_vendor')=='microsoft').with_columns(pl.col('notes').str.extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)').alias('canonical_cve'))
assert kev['canonical_cve'].null_count()==0
targets=set(kev['canonical_cve'])
# Recover encodings after removing a single inserted noise fragment. Search
# bounded numeric fields to prevent partial identifiers from becoming matches.
patterns=[
 ('normal',r'(?:CVE[-_:]|cve[-_:])?(\d{4})[-_:]{1,2}(\d{4,7})(?!\d)'),
 ('k',r'k(\d{4})(\d{7})(?!\d)'),
 ('i',r'i(\d{11})(?!\d)'),
 ('ri',r'ri(\d{11})(?!\d)'),
 ('h',r'h([0-9a-f]{3})x([0-9a-f]+)'),
 ('z',r'z([0-9a-z]+)\.(\d{4})(?!\d)'),
 ('b36',r'b36y([0-9a-z]{3})n([0-9a-z]+)'),
 ('bm',r'b36mix([0-9a-z]+)_(\d+)(?!\d)'),
 ('hex',r'hexmix([0-9a-f]+)_(\d+)(?!\d)'),
 ('rv',r'rv(\d{4})-(\d{4,7})(?!\d)'),
 ('off',r'off(\d{4})\.(\d+)(?!\d)'),
 ('yr',r'yr(\d+)_n(\d+)(?!\d)'),
 ('n',r'n(\d+)_y(\d+)(?!\d)'),
 ('tri',r'tri(\d{4})-(\d+)(?!\d)'),
 ('win',r'win\+(\d+)/(\d+)(?!\d)'),
 ('fold',r'fold(\d{4})-(\d{7})(?!\d)'),
 ('swap',r'swap(\d{3})-(\d{4})-(\d{4})(?!\d)'),
 ('mx',r'mx(\d{2})-(\d{2})-(\d{2})-(\d+)(?!\d)'),
 ('sp',r'sp(\d{2})_(\d{2})_(\d+)_(\d{2})(?!\d)'),
 ('p',r'p(\d{2})(\d{2})\.(\d{2})\.(\d+)(?!\d)'),
 ('ocr',r'(?:ocrCVE|ob)([0-9OIZSGB]{4})-?([0-9OIZSGB]{4,7})(?![0-9OIZSGB])'),
 ('ocrx',r'ocrx([0-9OIZSGB]{4})_([0-9OIZSGB]+)(?![0-9OIZSGB])'),
 ('ord',r'ord(\d{2})\.(\d{7})(?!\d)'),
 ('dot',r'dot([0-9.]+)'),
]
patterns=[(name,re.compile(p)) for name,p in patterns]
ocr=str.maketrans('OIZSGB','012568')
def decode(s):
 found=set()
 variants=set()
 if 'ABwot' in s: variants.add(s.replace('ABwot',''))
 # Noise contains uppercase letters and a punctuation mark, with total
 # length 5--7, regardless of its insertion point inside the payload.
 punctuation=r'[!@#$%&?~]'
 noise_patterns=[r'[A-P]{2}'+punctuation+r'[a-z0-9]{3}',r'[a-z0-9]{3}'+punctuation+r'[A-P]{2}',r'[a-z0-9]{3}'+punctuation+r'[A-P]{3}',r'[A-P]'+punctuation+r'[a-z0-9]{3}[A-P]',r'[A-P]{2}[0-9]{2}'+punctuation+r'[A-P]',r'[0-9]{2}'+punctuation+r'[A-P]{2}[a-z0-9A-P]',r'[A-P]{2}'+punctuation+r'[A-P]{3}',r'[A-P]{3}'+punctuation+r'[0-9]{2}',punctuation+r'[A-P]{2}[a-z0-9]{3}']
 for pattern in noise_patterns:
  for match in re.finditer('(?=('+pattern+'))',s):
   i=match.start(); variants.add(s[:i]+s[i+len(match[1]):])
 for v in variants:
  uppercase_check=re.sub(r'(?:ocrCVE|ob|ocrx)[0-9OIZSGB_\-]+','',v).replace('CVE','')
  if re.search('[A-Z]',uppercase_check): continue
  for name,pat in patterns:
   for m in pat.finditer(v):
    g=m.groups()
    try:
     if name=='normal': y,n=map(int,g)
     elif name=='k': y,n=map(int,g)
     elif name in ('i','ri'):
      t=g[0]; ys=t[:8:2]; ns=t[1:8:2]+t[8:]; y=int(ys[::-1] if name=='ri' else ys); n=int(ns[::-1] if name=='ri' else ns)
     elif name=='h':
      y=int(g[0],16)
      for end in (len(g[1]),len(g[1])-3):
       if end<=0: continue
       candidate=f'CVE-{y:04d}-{int(g[1][:end],16):04d}'
       if candidate in targets: found.add(candidate)
      continue
     elif name=='z':
      y=int(g[1][::-1]); n=int(g[0],36)-y
     elif name=='b36':
      y=int(g[0],36)
      for end in (len(g[1]),len(g[1])-3):
       if end<=0: continue
       candidate=f'CVE-{y:04d}-{int(g[1][:end],36):04d}'
       if candidate in targets: found.add(candidate)
      continue
     elif name=='bm': y,n=1990+int(g[0],36),int(g[1][::-1])
     elif name=='hex': y,n=1970+int(g[1]),int(g[0],16)
     elif name=='rv': y,n=int(g[0][::-1]),int(g[1][::-1])
     elif name=='off': y,n=int(g[0])-37,int(g[1])-7919
     elif name=='yr': y,n=int(g[0])+1999,int(g[1])-17
     elif name=='n': y,n=int(g[1])+1900,int(g[0])-100000
     elif name=='tri':
      a,b=map(int,g)
      if (a-2)%3 or (b-4)%5: continue
      y,n=(a-2)//3,(b-4)//5
     elif name=='win':
      a,b=map(int,g)
      if (b-1)%3: continue
      y,n=a+2010,(b-1)//3
     elif name=='fold': y,n=int(g[0][:2]+g[1][:2]),int(g[1][2:]+g[0][2:])
     elif name=='swap': y,n=int(g[1]),int(g[0]+g[2])
     elif name=='mx': y,n=int(g[0]+g[2]),int(g[1]+g[3])
     elif name=='sp': y,n=int(g[3]+g[1]),int(g[0]+g[2])
     elif name=='p':
      y,n=int(g[2]+g[0]),int(g[3])
      if n%97!=int(g[1]): continue
     elif name in ('ocr','ocrx'):
      y,n=(int(x.translate(ocr)) for x in g)
      if name=='ocrx': y-=101; n-=202
     elif name=='ord': y,n=2000+int(g[0]),int(g[1])
     elif name=='dot':
      t=g[0].replace('.',''); y,n=int(t[:4]),int(t[4:])
     c=f'CVE-{y:04d}-{n:04d}'
     if c in targets: found.add(c)
    except (ValueError,IndexError): pass
 return sorted(found)
if __name__=='__main__':
 # Validate recovery against independent canonical KEV NVD links.
 checks=kev.with_columns(pl.col('cve_ref').map_elements(decode,return_dtype=pl.List(pl.String)).alias('decoded'))
 failed=checks.filter(~pl.col('decoded').list.contains(pl.col('canonical_cve')))
 assert failed.height==0, failed
 print('KEV recovery failures:',failed.height)
 print(failed.select('cve_ref','canonical_cve').to_dicts())
 scores=read('vulns_db/cvss_metadata.parquet').with_columns(pl.col('score_text').str.extract(r'(\d+(?:\.\d+)?)').cast(pl.Float64).alias('score')).filter(pl.col('score')>=9.0)
 print('High-score rows:',scores.height,flush=True)
 scores=scores.with_columns(pl.col('cve_id').map_elements(decode,return_dtype=pl.List(pl.String)).alias('canonical_cve'))
 assert scores.filter(pl.col('canonical_cve').list.len()>1).height==0
 scores.write_parquet('/workspace/work/decoded_scores.parquet')
 matches=scores.explode('canonical_cve').drop_nulls('canonical_cve').join(kev,on='canonical_cve')
 products=matches.with_columns(pl.col('products_csv').str.split(',').alias('product')).explode('product').with_columns(pl.col('product').str.strip_chars().str.to_lowercase()).filter(pl.col('product')!='').select('product').unique().sort('product')
 products.write_csv('/workspace/work/products.csv')
 matches.write_parquet('/workspace/work/matches.parquet')
 answer=products.height
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(answer)}))
 print(products,answer)
