import re,json
from pathlib import Path
import ibis

# Inserted noise is removed before parsing the source wrappers.
NOISE = [r'[A-P]{2}\d{2}[%?][A-P]',r'[A-P][!$][a-z0-9]{3}[A-P]',r'[a-z0-9]{3}[#&][A-P]{3}',r'[a-z0-9]{3}[#&][A-P]{2}',r'[a-z0-9]{3}[~@][A-P]{2}',r'[A-P]{2}[~@][A-P]{3}',r'[A-P]{3}[!$]\d{2}',r'\d{3}[%?][A-P]{3}',r'\d{2}[%?][A-P]{2}[a-z0-9]',r'[A-P]{2}[!#$&]\d{3}',r'[~@][A-P]{2}[a-z0-9]{3}']

def unwrap(s):
 s=re.sub(r'^[a-z]+-[a-p]+(?:::id=|::ref=|::key=|~~|[~/#%@|$]|=>|--|__|\+\+|::)+','',s)
 s=re.sub(r'^(?:(?:doc|id|raw|key|join|slot|ctx):)?[<({\[]?[a-p]{3}(?:::|[/~:#@|])?','',s)
 explicit=bool(re.search(r':(?:join|slot|raw|doc|key|ctx|id)[a-p]{3}(?=[^a-z]|$)',s))
 s=re.split(r':(?:join|slot|raw|doc|key|ctx|id)[a-p]{3}(?=[^a-z]|$)|(?:::aux=|::end=|::via=|=>|--|__|\+\+|~~|::|[#/@~%|$])(?:[a-z]+)-[a-p]+$',s)[0]

 if not explicit:s=re.sub(r'[>)}\]]?[a-p]{3}$','',s)
 return s.strip('<>(){}[]')

def parse(s):
 def m(p): return re.fullmatch(p,s)
 ocr=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
 if x:=m(r'(?:[Cc][Vv][Ee][-_:])?(\d{4})[-_:]+(\d+)'): y,n=map(int,x.groups())
 elif x:=m(r'off(\d+)\.(\d+)'): y,n=int(x[1])-37,int(x[2])-7919
 elif x:=m(r'win\+(\d+)/(\d+)'): y,n=int(x[1])+2010,(int(x[2])-1)//3
 elif x:=m(r'tri(\d+)-(\d+)'): y,n=(int(x[1])-2)//3,(int(x[2])-4)//5
 elif x:=m(r'n(\d+)_y(\d+)'): y,n=int(x[2])+1900,int(x[1])-100000
 elif x:=m(r'yr(\d+)_n(\d+)'): y,n=int(x[1])+1999,int(x[2])-17
 elif x:=m(r'ord(\d+)\.(\d+)'): y,n=int(x[1])+2000,int(x[2])
 elif x:=m(r'k(\d{4})(\d+)'): y,n=int(x[1]),int(x[2])
 elif x:=m(r'ocrCVE([0-9OIZSGB]{4})([0-9OIZSGB]+)'): y,n=int(x[1].translate(ocr)),int(x[2].translate(ocr))
 elif x:=m(r'ob([0-9OIZSGB]{4})-([0-9OIZSGB]+)'): y,n=int(x[1].translate(ocr)),int(x[2].translate(ocr))
 elif x:=m(r'ocrx([0-9OIZSGB]{4})_([0-9OIZSGB]+)'): y,n=int(x[1].translate(ocr))-101,int(x[2].translate(ocr))-202
 elif x:=m(r'rv(\d{4})-(\d+)'): y,n=int(x[1][::-1]),int(x[2][::-1])
 elif x:=m(r'p(\d{2})\d{2}\.(\d{2})\.(\d+)'): y,n=int(x[2]+x[1]),int(x[3])
 elif x:=m(r'fold(\d{2})(\d{2})-(\d{2})(\d+)'): y,n=int(x[1]+x[3]),int(x[4]+x[2])
 elif x:=m(r'swap(\d+)-(\d{4})-(\d+)'): y,n=int(x[2]),int(x[1]+x[3])
 elif x:=m(r'sp(\d+)_(\d{2})_(\d+)_(\d{2})'): y,n=int(x[4]+x[2]),int(x[1]+x[3])
 elif x:=m(r'mx(\d{2})-(\d+)-(\d{2})-(\d+)'): y,n=int(x[1]+x[3]),int(x[2]+x[4])
 elif x:=m(r'h([0-9a-f]+)x([0-9a-f]+)'): y,n=int(x[1],16),int(x[2],16)
 elif x:=m(r'hexmix([0-9a-f]+)_([0-9a-f]+)'): y,n=int(x[2])+1970,int(x[1],16)
 elif x:=m(r'b36y([0-9a-z]{3})n([0-9a-z]+)'): y,n=int(x[1],36),int(x[2],36)
 elif x:=m(r'b36mix([0-9a-z]+)_(\d+)'): y,n=int(x[1],36)+1990,int(x[2][::-1])
 elif x:=m(r'z([0-9a-z]+)\.(\d{4})'): y,n=int(x[2][::-1]),int(x[1],36)-int(x[2][::-1])
 elif x:=m(r'dot([\d.]+)'): d=x[1].replace('.','');y,n=int(d[:4]),int(d[4:])
 elif x:=m(r'(ri|i)(\d+)'):
  d=x[2]; ys=''.join(d[i] for i in (0,2,4,6)); ns=''.join(d[i] for i in (1,3,5,7))+d[8:]
  if x[1]=='ri':ys,ns=ys[::-1],ns[::-1]
  y,n=int(ys),int(ns)
 else:return None
 if not(1990<=y<=2035 and 0<n<10000000):return None
 return f'CVE-{y}-{n:04d}'

def options(raw):
 out=[]
 for p in NOISE:
  for m in re.finditer(p,raw):
   fragment=m[0]
   s=unwrap(raw[:m.start()]+raw[m.end():])
   try:v=parse(s)
   except (ValueError,IndexError):v=None
   if v:out.append((v,fragment))
 return out

def candidates(raw):
 return sorted(set(v for v,f in options(raw)))

@ibis.udf.scalar.python
def decode_options(raw: str) -> list[str]:
 return list(set(v+'|'+f for v,f in options(raw)))

def main():
 con=ibis.duckdb.connect()
 kev=con.read_parquet('/workspace/data/kev_db/kev_entries.parquet')
 nvd=con.read_parquet('/workspace/data/vulns_db/cves.parquet')
 keys=kev.select(raw=kev.cve_ref).union(nvd.select(raw=nvd.cve_id),distinct=True)
 decoded=keys.mutate(option=decode_options(keys.raw)).unnest('option')
 decoded=decoded.mutate(canonical=decoded.option.split('|')[0], noise=decoded.option.split('|')[1]).drop('option')
 frequencies=decoded.group_by('noise').aggregate(frequency=decoded.raw.nunique())
 ranked=decoded.join(frequencies,'noise').select(decoded.raw,decoded.canonical,decoded.noise,frequencies.frequency)
 ranked=ranked.mutate(rank=ibis.row_number().over(ibis.window(group_by=ranked.raw,order_by=[ranked.frequency.desc(),ranked.canonical])))
 mapping=ranked.filter(ranked.rank==0).select('raw','canonical')
 assert keys.count().execute()==mapping.count().execute(), 'Unparsed identifiers'
 # Repeated noise fragments resolve competing placements; preserve this audit.
 ranked.to_parquet('/workspace/work/decoding_audit.parquet')
 kev_keys=kev.join(mapping,kev.cve_ref==mapping.raw).select(kev.cve_ref,kev.notes,mapping.canonical)
 nvd_keys=nvd.join(mapping,nvd.cve_id==mapping.raw).select(mapping.canonical).distinct()
 note_key=kev_keys.notes.re_extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)',1)
 mismatches=kev_keys.filter((note_key!='') & (note_key!=kev_keys.canonical))
 print('KEV note mismatches:',mismatches.to_pyarrow().to_pylist())
 assert mismatches.count().execute()==0
 missing=kev_keys.anti_join(nvd_keys,'canonical')
 missing.to_parquet('/workspace/work/unmatched_entries.parquet')
 count=int(missing.count().execute())
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':f'{count} entries.'})+'\n')
 print('Unmatched KEV entries:',count)

if __name__=='__main__':main()
