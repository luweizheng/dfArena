import re,json
from pathlib import Path
import polars as pl
ROOT=Path('/workspace/data')
noise=re.compile(r'[~@][A-P]{2}[a-z0-9]{3}|[A-P][!$][a-z0-9]{3}[A-P]|[A-P]{2}\d{2}[?%][A-P]|\d{2}[?%][A-P]{2}[a-z0-9]|[A-P]{3}[!$&]\d{2}|[A-P]{2}[!#$&]\d{3}|\d{3}[?%&][A-P]{3}|[A-P]{2}[~@][A-P]{3}|[a-z0-9]{3}[#&][A-P]{3}|[a-z0-9]{3}[#@&~][A-P]{2}(?![a-z])')
def clean(s):return noise.sub('',s)
ocr=str.maketrans('OIZSGB','012568')
def decode_core(s):
 s=re.sub(r"[a-p]{3}(?=(?:::|--|~~|__|\+\+|[~@#$%/|])(?:aux=|via=|end=)?(?:trail|note|leaf|slot|mark|tag|seen|edge|sink|cache|trace|frag|node|tail|batch|src)-)", "", s)
 patterns=[
 (r'(?:CVE[-_]|cve[-:])?(20\d{2}|199\d)[-_:]{1,2}(\d+)',lambda a,b:(int(a),int(b))),
 (r'k(20\d{2}|199\d)(\d{7})',lambda a,b:(int(a),int(b))),
 (r'rv(\d{4})-(\d+)',lambda a,b:(int(a[::-1]),int(b[::-1]))),
 (r'off(\d{4})\.(\d+)',lambda a,b:(int(a)-37,int(b)-7919)),
 (r'tri(\d+)-(\d+)',lambda a,b:((int(a)-2)//3,(int(b)-4)//5)),
 (r'win\+(\d+)/(\d+)',lambda a,b:(int(a)+2010,(int(b)-1)//3)),
 (r'b36y([0-9a-z]{3})n([0-9a-z]+)',lambda a,b:(int(a,36),int(b,36))),
 (r'h([0-9a-f]+)x([0-9a-f]+)',lambda a,b:(int(a,16),int(b,16))),
 (r'hexmix([0-9a-f]+)_(\d+)',lambda a,b:(int(b)+1970,int(a,16))),
 (r'b36mix([0-9a-z]+)_(\d{7})',lambda a,b:(int(a,36)+1990,int(b[::-1]))),
 (r'n(\d+)_y(\d+)',lambda a,b:(int(b)+1900,int(a)-100000)),
 (r'yr(\d+)_n(\d+)',lambda a,b:(int(a)+1999,int(b)-17)),
 (r'ord(\d+)\.(\d{7})',lambda a,b:(int(a)+2000,int(b))),
 (r'p(\d{2})\d{2}\.(\d{2})\.(\d+)',lambda a,b,c:(int(b+a),int(c))),
 (r'swap(\d{3})-(\d{4})-(\d{4})',lambda a,b,c:(int(b),int(a+c))),
 (r'sp(\d+)_(\d{2})_(\d+)_20',lambda a,b,c:(2000+int(b),int(a+c))),
 (r'ri(\d{11})',lambda a:(int(a[:8:2][::-1]),int((a[1:8:2]+a[8:])[::-1]))),
 (r'fold(\d{4})-(\d{7})',lambda a,b:(2000+int(b[:2]),int(b[2:])*100+int(a)-2000)),
 (r'z([0-9a-z]+)\.(\d{4})',lambda a,b:(int(b[::-1]),int(a,36)-int(b[::-1]))),
 (r'mx(\d{2})-(\d{2})-(\d{2})-(\d+)',lambda a,b,c,d:(int(a+c),int(b+d))),
 (r'ocrx([0-9OIZSGB]+)_([0-9OIZSGB]+)',lambda a,b:(int(a.translate(ocr))-101,int(b.translate(ocr))-202)),
 (r'ob([0-9OIZSGB]{4})-([0-9OIZSGB]+)',lambda a,b:(int(a.translate(ocr)),int(b.translate(ocr)))),
 (r'ocrCVE([0-9OIZSGB]{4})([0-9OIZSGB]{4,7})',lambda a,b:(int(a.translate(ocr)),int(b.translate(ocr)))),
 (r'dot([0-9.]+)',lambda a:(int(a.replace('.','')[:4]),int(a.replace('.','')[4:]))) ]
 # Encoded forms must precede plain numeric matches embedded in them.
 patterns=[(r'i(\d{11})',lambda a:(int(a[:8:2]),int(a[1:8:2]+a[8:])))]+patterns[2:]+patterns[:2]
 for pat,fn in patterns:
  m=re.search(pat,s)
  if m:
   try:
    y,n=fn(*m.groups())
    if 1990<=y<=2035 and 0<n<10000000:return f'CVE-{y}-{n:04d}'
   except ValueError:pass
 return None

noise_patterns=[re.compile(p.replace('(?![a-z])','')) for p in noise.pattern.split('|')]
KEV_KEYS=set()
def decode(s):
 candidates=[]
 for p in noise_patterns:
  for m in p.finditer(s):
   value=decode_core(s[:m.start()]+s[m.end():])
   if value:
    if value in KEV_KEYS:return value
    candidates.append(value)
 return candidates[0] if candidates else decode_core(s)

def product(s):
 if s.startswith('cpe:'):return s.split(':')[3:5]
 if '/' in s:
  a,b=s.split('/',1);return [a,b.split('@')[0].lower()]
 a,b=s.split(' ',1);return [a,b.rsplit(' ',1)[0].lower().replace(' ','_')]

if __name__=='__main__':
 k=pl.read_parquet(ROOT/'kev_db/kev_entries.parquet')
 KEV_KEYS.update(k['notes'].str.extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)').drop_nulls().to_list())
 check=k.with_columns(pl.col('cve_ref').map_elements(decode,return_dtype=pl.String).alias('decoded'),pl.col('notes').str.extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)').alias('expected'))
 print('KEV validation',check.filter(pl.col('decoded')==pl.col('expected')).height,'/',k.height)
 check.filter(pl.col('decoded').is_null()|(pl.col('decoded')!=pl.col('expected'))).select('cve_ref','decoded','expected').write_csv('/workspace/work/decode_errors.csv')
 c=pl.read_parquet(ROOT/'cpe_db/cpe_matches.parquet').filter(pl.col('vulnerable_flag').str.to_lowercase().is_in(['true','t','1','yes','y','v','vulnerable','affected']))
 keys=c.select('cve_id').unique().with_columns(pl.col('cve_id').map_elements(decode,return_dtype=pl.String).alias('key'))
 c=c.join(keys,on='cve_id').with_columns(pl.col('criteria').map_elements(product,return_dtype=pl.List(pl.String)).alias('parts')).with_columns(pl.col('parts').list.get(0).alias('alias'),pl.col('parts').list.get(1).alias('product'))
 c=c.join(pl.read_parquet(ROOT/'cpe_db/vendor_aliases.parquet'),on='alias',how='left')
 kev=check.select(pl.coalesce('expected','decoded').alias('key')).drop_nulls().unique()
 counts=c.join(kev,on='key',how='semi').group_by('canonical_vendor','product').len().sort('len',descending=True)
 c.filter(pl.col('key').is_null()).group_by('canonical_vendor','product').len().sort('len',descending=True).write_csv('/workspace/work/unresolved.csv');print(counts.head(15));print('undecoded',keys['key'].null_count())
 counts.write_csv('/workspace/work/counts.csv')
 r=counts.row(0,named=True)
 unresolved=c.filter(pl.col('key').is_null()).group_by('canonical_vendor','product').len().rename({'len':'unresolved'})
 bounds=counts.join(unresolved,on=['canonical_vendor','product'],how='full',coalesce=True).with_columns((pl.col('len').fill_null(0)+pl.col('unresolved').fill_null(0)).alias('upper'))
 competitors=bounds.filter((pl.col('canonical_vendor')!=r['canonical_vendor']) | (pl.col('product')!=r['product']))
 assert competitors['upper'].max()<r['len'], 'Unresolved rows could change the winner'
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':r['canonical_vendor'].lower()+':'+r['product'].lower()}))
