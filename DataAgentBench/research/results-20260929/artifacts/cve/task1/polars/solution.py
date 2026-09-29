import re,json
from functools import lru_cache
from pathlib import Path
import polars as pl
ROOT=Path('/workspace/data')
def read(p):return pl.read_parquet(ROOT/(p+'.parquet'))

def core(s):
 s=re.sub(r'^[a-z]+-[a-p]{5}', '',s)
 s=re.sub(r'^(?:::ref=|::key=|::id=|::)?','',s)
 s=re.sub(r'^[^a-zA-Z0-9]*','',s)
 s=re.sub(r'^(?:doc|raw|id|key|slot|join|ctx):','',s)
 s=re.sub(r'^[a-p]{3}(?:::|[~@#/:|])?','',s)
 s=s.replace('=>','@@')
 s=re.split(r':(?:doc|raw|id|key|slot|join|ctx)[a-p]{3}|[\]}>)]',s)[0]
 s=re.sub(r'[a-p]{3}(?=::|=>|[~@#/$%|]|--|\+\+|__).*$', '',s)
 s=re.split(r'(?:::|=>|--|\+\+|__|[~@#/$%|])(?:aux=|end=|via=)?(?:src|leaf|tag|trace|frag|node|trail|sink|seen|batch|mark|cache|edge|note|tail|slot)-',s)[0]
 return s

OCR=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
@lru_cache(None)
def decode_core(c):
 try:
  if c.startswith('ocrCVE'):
   d=c[6:].translate(OCR);y,n=int(d[:4]),int(d[4:])
  elif c.startswith('ob'):
   a,b=c[2:].translate(OCR).split('-');y,n=int(a),int(b)
  elif c.startswith('ocrx'):
   a,b=c[4:].translate(OCR).split('_');y,n=int(a)-101,int(b)-202
  elif re.fullmatch(r'(?:[Cc][Vv][Ee][:_-])?\d{4}(?:::|[:_-])\d+',c):
   a,b=re.sub(r'^[Cc][Vv][Ee][:_-]','',c).replace('::',':').replace('_',':').replace('-',':').split(':');y,n=int(a),int(b)
  elif c.startswith('off'):
   a,b=c[3:].split('.');y,n=int(a)-37,int(b)-7919
  elif c.startswith('win+'):
   a,b=c[4:].split('/');y,n=int(a)+2010,(int(b)-1)//3
  elif c.startswith('tri'):
   a,b=c[3:].split('-');y,n=(int(a)-2)//3,(int(b)-4)//5
  elif c.startswith('yr'):
   a,b=c[2:].split('_n');y,n=int(a)+1999,int(b)-17
  elif c.startswith('ord'):
   a,b=c[3:].split('.');y,n=int(a)+2000,int(b)
  elif c.startswith('n'):
   a,b=c[1:].split('_y');y,n=int(b)+1900,int(a)-100000
  elif c.startswith('rv'):
   a,b=c[2:].split('-');y,n=int(a[::-1]),int(b[::-1])
  elif c.startswith('k'):
   y,n=int(c[1:5]),int(c[5:])
  elif c.startswith('dot'):
   d=c[3:].replace('.','');y,n=int(d[:4]),int(d[4:])
  elif c.startswith('h') and not c.startswith('hexmix'):
   a,b=c[1:].split('x');y,n=int(a,16),int(b,16)
  elif c.startswith('hexmix'):
   a,b=c[6:].split('_');y,n=int(b)+1970,int(a,16)
  elif c.startswith('b36y'):
   a,b=c[4:].split('n',1);y,n=int(a,36),int(b,36)
  elif c.startswith('b36mix'):
   a,b=c[6:].split('_');y,n=int(a,36)+1990,int(b[::-1])
  elif c.startswith('z'):
   a,b=c[1:].split('.');y=int(b[::-1]);n=int(a,36)-y
  elif c.startswith('p'):
   a,b,d=c[1:].split('.');y,n=int(b)*100+int(a[:2]),int(d)
  elif c.startswith('sp'):
   a,b,d,e=c[2:].split('_');y,n=int(e+b),int(a+d)
  elif c.startswith('mx'):
   a,b,d,e=c[2:].split('-');y,n=int(a+d),int(b+e)
  elif c.startswith('swap'):
   a,b,d=c[4:].split('-');y,n=int(b),int(a+d)
  elif c.startswith('fold'):
   a,b=c[4:].split('-');y,n=int(a[:2]+b[:2]),int(b[2:]+a[2:])
  elif c.startswith('i') or c.startswith('ri'):
   d=c[2:] if c.startswith('ri') else c[1:];a,b=d[:8:2],d[1:8:2]+d[8:];y,n=(int(a[::-1]),int(b[::-1])) if c.startswith('ri') else (int(a),int(b))
  else:return None
  if not 1990<=y<=2030 or not 0<n<10000000:return None
  return f'CVE-{y}-{n:04d}'
 except (ValueError,IndexError):return None


PATTERNS=[r'[A-P][!$][a-z0-9]{3}[A-P]',r'[A-P]{2}\d{2}[?%][A-P]',r'\d{2}[?%][A-P]{2}[a-z0-9]',r'[A-P]{2}[!#$&]\d{3}',r'\d{3}[&?%#][A-P]{3}',r'[A-P]{3}[!$]\d{2}',r'[a-z0-9]{3}[~@&#][A-P]{2}',r'[a-z0-9]{3}[~@&#][A-P]{3}',r'[A-P]{2}[~@][A-P]{3}',r'[~@][A-P]{2}[a-z0-9]{3}']
@lru_cache(None)
def candidates(s):
 # Remove the single inserted fragment, trying overlapping forms separately.
 out=set()
 for p in PATTERNS:
  for m in re.finditer('(?=('+p+'))',s):
   cleaned=s[:m.start()]+s[m.start()+len(m[1]):]
   d=decode_core(core(cleaned))
   if d:out.add(d)
 return sorted(out)
if __name__=='__main__':
    # KEV notes provide an independent check on decoding its noisy join keys.
    kev=read('kev_db/kev_entries').with_columns(
        pl.col('cve_ref').map_elements(candidates,return_dtype=pl.List(pl.String)).alias('ids'),
        pl.col('notes').str.extract(r'nvd.nist.gov/vuln/detail/(CVE-\d+-\d+)').alias('id'))
    assert kev['id'].null_count()==0
    assert kev.filter(~pl.col('ids').list.contains(pl.col('id'))).is_empty()
    kev_ids=kev.select('id').unique()
    aliases=read('cpe_db/vendor_aliases').filter(pl.col('canonical_vendor')=='apache')
    apache=read('cpe_db/cpe_matches').with_columns(
        pl.col('criteria').str.extract(r'^(?:cpe:2\.3:[^:]+:)?([^:/ ]+)').alias('alias')
    ).join(aliases,on='alias').filter(
        pl.col('vulnerable_flag').str.strip_chars().str.to_lowercase().is_in(
            ['true','t','1','yes','y','v','vulnerable','affected'])
    ).with_columns(pl.col('cve_id').map_elements(candidates,return_dtype=pl.List(pl.String)).alias('ids'))
    registry=read('vulns_db/cves').with_columns(
        pl.col('cve_id').map_elements(candidates,return_dtype=pl.List(pl.String)).alias('ids'))
    assert apache.filter(pl.col('ids').list.len()==0).is_empty()
    assert registry.filter(pl.col('ids').list.len()==0).is_empty()
    # Ambiguous fragment removals cannot affect the count: all Apache/KEV
    # configurations and their registry records must decode uniquely.
    configurations=apache.with_columns(pl.col('ids').list.len().alias('candidate_count')).explode('ids').rename({'ids':'id'}).join(kev_ids,on='id')
    assert configurations.filter(pl.col('candidate_count')!=1).is_empty()
    relevant=registry.with_columns(pl.col('ids').list.len().alias('candidate_count')).explode('ids').rename({'ids':'id'}).join(configurations.select('id').unique(),on='id')
    assert relevant.filter(pl.col('candidate_count')!=1).is_empty()
    # A qualifying publication record suffices; retain distinct identifiers
    # after filtering, including when the registry contains duplicate rows.
    result=relevant.filter(pl.col('published').str.starts_with('2023-')).select('id').unique().sort('id')
    result.write_csv('/workspace/work/matched_cves.csv')
    count=result.height
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(count)}))
    print(f'Distinct qualifying CVEs: {count}')
