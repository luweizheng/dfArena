import re,json
from functools import lru_cache
import ibis
from ibis.expr.datatypes import String

# Extract the payload from the source envelope; source tags are unrelated to CVE identity.
def core(s):
 s=re.sub(r'^[a-z]+-[a-p]{5}', '', s)
 s=re.sub(r'^(?:(?:::)?(?:ref|id|key|raw|slot|doc|join|ctx)[:=]|[^a-z])*','',s)
 s=re.sub(r'^[a-p]{3}(?:::|[~|@/#:])?', '',s)
 s=re.split(r':(?:id|key|raw|slot|doc|join|ctx)[a-p]{3}',s)[0]
 s=re.split(r'(?:::|~~|__|=>|\+\+|--|[~|@/#%$])(?:aux=|via=|end=)?(?:trail|trace|leaf|edge|node|slot|sink|cache|mark|seen|frag|tag|tail|batch|note|src)-',s)[0]
 return re.sub(r'[>\])}][a-p]{3}$','',s)

def parse(s):
 pats=[(r'(?:cve[-_:]|CVE[-_])?(\d{4})[-_:]{1,2}(\d+)',lambda a,b:(int(a),int(b))),
 (r'k(\d{4})(\d{7})',lambda a,b:(int(a),int(b))),
 (r'rv(\d{4})-(\d+)',lambda a,b:(int(a[::-1]),int(b[::-1]))),
 (r'off(\d+)\.(\d+)',lambda a,b:(int(a)-37,int(b)-7919)),
 (r'win\+(\d+)/(\d+)',lambda a,b:(int(a)+2010,(int(b)-1)//3) if int(b)%3==1 else (0,0)),
 (r'tri(\d+)-(\d+)',lambda a,b:((int(a)-2)//3,(int(b)-4)//5) if int(a)%3==2 and int(b)%5==4 else (0,0)),
 (r'ord(\d+)\.(\d+)',lambda a,b:(int(a)+2000,int(b))),
 (r'yr(\d+)_n(\d+)',lambda a,b:(int(a)+1999,int(b)-17)),
 (r'n1(\d+)_y1(\d+)',lambda a,b:(int(b)+2000,int(a))),
 (r'z([0-9a-z]+)\.(\d{4})',lambda a,b:(int(b[::-1]),int(a,36)-int(b[::-1]))),
 (r'b36y([0-9a-z]+?)n([0-9a-z]+)',lambda a,b:(int(a,36),int(b,36))),
 (r'hexmix([0-9a-f]+)_([0-9a-f]+)',lambda a,b:(int(b)+1970,int(a,16))),
 (r'b36mix([0-9a-z]+)_(\d+)',lambda a,b:(int(a,36)+1990,int(b[::-1]))),
 (r'fold(\d{2})(\d{2})-(\d{2})(\d+)',lambda a,b,c,d:(int(a+c),int(d+b))),
 (r'swap(\d+)-(\d{4})-(\d+)',lambda a,b,c:(int(b),int(a+c))),
 (r'p(\d{2})\d{2}\.(\d{2})\.(\d+)',lambda a,b,c:(int(b+a),int(c))),
 (r'mx(\d{2})-(\d+)-(\d{2})-(\d+)',lambda a,b,c,d:(int(a+c),int(b+d))),
 (r'sp(\d+)_(\d{2})_(\d+)_(\d{2})',lambda a,b,c,d:(int(d+b),int(a+c))),
 (r'ri(\d+)',lambda a:(int(a[:8:2][::-1]),int((a[1:8:2]+a[8:])[::-1]))),
 (r'i(\d+)',lambda a:(int(a[:8:2]),int(a[1:8:2]+a[8:]))),
 (r'dot([0-9.]+)',lambda a:(int(a.replace('.','')[:4]),int(a.replace('.','')[4:]))),
 (r'h([0-9a-f]{3})x([0-9a-f]+)',lambda a,b:(int(a,16),int(b,16))),
 ]
 if s.startswith(('ob','ocr')):
  s=s.translate(str.maketrans('OZISBG','021586'))
  if s.startswith('ob'):s=s[2:]
  elif s.startswith('ocrCVE'):s=s[6:10]+'-'+s[10:]
  elif s.startswith('ocrx'):
   m=re.fullmatch(r'ocrx(\d+)_(\d+)',s)
   if not m:return None
   return valid(int(m[1])-101,int(m[2])-202)
 for p,f in pats:
  m=re.fullmatch(p,s)
  if m:
   try:return valid(*f(*m.groups()))
   except ValueError:return None
 return None

def valid(y,n):
 return f'CVE-{y}-{n:04d}' if 1990<=y<=2030 and 0<n<10000000 else None

@lru_cache(maxsize=None)
def candidates(s):
 s=core(s);out=set()
 if re.match(r'^[A-P]{2}[a-z0-9]{3}',s):
  x=parse(s[5:])
  if x:out.add(x)
 for n in (6,7):
  for i in range(len(s)-n+1):
   noise=s[i:i+n]
   if re.fullmatch(r'(?:[A-P]{2}[!#$&][0-9]{3}|[A-P]{2}[~@][A-P]{3}|[A-P]{2}[0-9]{2}[?%][A-P]|[A-P]{3}[!$][0-9]{2}|[0-9]{3}[?%&][A-P]{3}|[a-z0-9]{3}[~@#&][A-P]{2,3}|[~@%][A-P]{2}[a-z0-9]{3}|[0-9]{2}[?%@][A-P]{2}[a-z0-9]|[A-P][!$][a-z0-9]{3}[A-P])',noise):
    x=parse(s[:i]+s[i+n:])
    if x:out.add(x)
    x=parse(re.sub(r'[a-p]{3}$','',s[:i]+s[i+n:]))
    if x:out.add(x)
 x=parse(s)
 if x:out.add(x)
 return sorted(out)

if __name__=='__main__':
 c=ibis.duckdb.connect()
 k=c.read_parquet('/workspace/data/kev_db/kev_entries.parquet')
 m=c.read_parquet('/workspace/data/cpe_db/cpe_matches.parquet')
 a=c.read_parquet('/workspace/data/cpe_db/vendor_aliases.parquet')
 # NVD URLs in the KEV catalog provide independent, unencoded membership keys.
 kev=k.mutate(key=k.notes.re_extract(r'https://nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)',1))
 keys=set(kev.key.to_pyarrow().to_pylist())-{None,''}
 print('KEV URL keys',len(keys),'missing',kev.filter(kev.key.isnull() | (kev.key=='')).count().execute(),flush=True)
 @ibis.udf.scalar.python
 def membership(s: str) -> str:
  cs=candidates(s)
  if not cs:return 'unknown'
  flags=[x in keys for x in cs]
  return 'yes' if all(flags) else ('maybe' if any(flags) else 'no')
 t=m.filter(m.vulnerable_flag.strip().lower().isin(['y','yes','true','1','t','v','affected','vulnerable']))
 t=t.mutate(alias=ibis.cases((t.criteria.startswith('cpe:'),t.criteria.split(':')[3]),else_=t.criteria.re_extract(r'^([^/ ]+)',1)),product=ibis.cases((t.criteria.startswith('cpe:'),t.criteria.split(':')[4]),(t.criteria.contains('/'),t.criteria.re_extract(r'^[^/]+/(.*)@',1)),else_=t.criteria.re_extract(r'^[^ ]+ (.*) [^ ]+$',1).replace(' ','_')).lower(),status=membership(t.cve_id))
 t=t.join(a,t['alias']==a['alias'])
 result=t.group_by(vendor=t.canonical_vendor,product=t.product).aggregate(lower=(t.status=='yes').sum(),upper=(t.status!='no').sum(),possible=(t.status.isin(['yes','maybe'])).sum()).order_by(ibis.desc('lower'))
 rows=result.to_pyarrow().to_pylist()
 print(rows[:15],flush=True)
 with open('/workspace/work/bounds.json','w') as f:json.dump(rows,f)
 best=rows[0]
 assert best['lower']>max(r['upper'] for r in rows[1:]), 'Need further decoding to resolve winner'
 with open('/workspace/work/answer.json','w') as f:json.dump({'answer':best['vendor']+':'+best['product']},f)
