import json,re
from pathlib import Path
import pandas as pd
ROOT=Path('/workspace/data')
def read(p): return pd.read_parquet(ROOT/(p+'.parquet'))
OCR=str.maketrans({'O':'0','Z':'2','I':'1','S':'5','G':'6','B':'8'})
def pair(y,n):
 y,n=int(y),int(n)
 if 1990<=y<=2035 and 0<n<10000000:return f'CVE-{y}-{n:04d}'
def packed(s):return pair(s[:4],s[4:])
# Each key contains one six-character infix, in addition to alphabetic wrappers.
# Try its possible positions, requiring that the entire remaining numeric payload
# matches a reversible encoding. Alphabetic wrappers have no digits/capitals.
rules=[
 (r'(?:cve[-:]|CVE_)?(20\d{2})[-_:]+(\d{4,7})',lambda a,b:pair(a,b)),
 (r'b36y([0-9a-z]+)n([0-9a-z]+)',lambda a,b:pair(int(a,36),int(b,36))),
 (r'rv(\d{4})-(\d+)',lambda a,b:pair(a[::-1],b[::-1])),
 (r'p(\d{2})\d{2}\.(\d{2})\.(\d+)',lambda a,b,c:pair(b+a,c)),
 (r'(?:ob|ocrCVE)([0-9OZISGB]{4})-?([0-9OZISGB]{4,7})',lambda a,b:pair(a.translate(OCR),b.translate(OCR))),
 (r'ocrx([0-9OZISGB]{4})_([0-9OZISGB]+)',lambda a,b:pair(int(a.translate(OCR))-101,int(b.translate(OCR))-202)),
 (r'ri(\d+)',lambda a:pair(a[:8:2][::-1],(a[1:8:2]+a[8:])[::-1])),
 (r'b36mix([0-9a-z]+)_(\d+)',lambda a,b:pair(int(a,36)+1990,b[::-1])),
 (r'yr(\d+)_n(\d+)',lambda a,b:pair(int(a)+1999,int(b)-17)),
 (r'swap(\d+)-(\d{4})-(\d+)',lambda a,b,c:pair(b,a+c)),
 (r'n(\d+)_y(\d+)',lambda a,b:pair(int(b)+1900,int(a)-100000)),
 (r'i(\d+)',lambda a:pair(a[:8:2],a[1:8:2]+a[8:])),
 (r'z([0-9a-z]+)\.(\d{4})',lambda a,b:pair(b[::-1],int(a,36))),
 (r'h([0-9a-f]+)x([0-9a-f]+)',lambda a,b:pair(int(a,16),int(b,16))),
 (r'hexmix([0-9a-f]+)_([0-9a-f]+)',lambda a,b:pair(int(b,16)+1940,int(a,16))),
 (r'dot([0-9.]+)',lambda a:packed(a.replace('.',''))),
 (r'k(\d+)q(\d+)',lambda a,b:pair(a,b)),
 (r'mx(\d{2})-(\d{2})-(\d{2})-(\d+)',lambda a,b,c,d:pair(a+c,b+d)),
 (r'fold(\d{2})(\d{2})-(\d{2})(\d+)',lambda a,b,c,d:pair(a+c,d+b)),
 (r'win\+(\d+)/(\d+)',lambda a,b:pair(int(a)+2010,(int(b)-1)//3)),
 (r'ord(\d+)\.(\d+)',lambda a,b:pair(int(a)+2000,b)),
 (r'k(\d{4})(\d{7})',lambda a,b:pair(a,b)),
 (r'tri(\d+)-(\d+)',lambda a,b:pair((int(a)-2)//3,(int(b)-4)//5)),
]
def decode(s):
 out=set()
 for length in (6,7):
  for i in range(len(s)-length+1):
   frag=s[i:i+length]
   if sum(c.isupper() for c in frag)<2 or sum(not c.isalnum() for c in frag)!=1:continue
   t=s[:i]+s[i+length:]
   for pat,fn in rules:
    for m in re.finditer(pat,t):
     if re.search(r'[0-9A-Z]',t[:m.start()]+t[m.end():]):continue
     try:
      result=fn(*m.groups())
      if result:out.add(result)
     except (ValueError,IndexError):pass
 return sorted(out)

def cpe(s):
 if s.startswith('cpe:'):p=s.split(':');return p[3],p[4].lower()
 if '/' in s:a,p=s.split('/',1);return a,p.split('@')[0].lower()
 a,p,_=s.split(' ',2);return a,p.lower()
def version(s):
 if pd.isna(s) or s=='*':return None
 if s.startswith('build-'):
  x=s[6:];assert x.isdigit() and len(x)%3==0
  return '.'.join(str(int(x[i:i+3])) for i in range(0,len(x),3))
 return re.sub('[,_]','.',s.removeprefix('v'))

m=read('cpe_db/cpe_matches'); a=read('cpe_db/vendor_aliases')
m[['alias','product']]=pd.DataFrame(m.criteria.map(cpe).tolist(),index=m.index)
m=m.merge(a,on='alias',validate='many_to_one')
m=m[(m.canonical_vendor=='apache')&(m['product']=='tomcat')&m.vulnerable_flag.str.lower().isin(['v','affected','vulnerable','y','yes','true','t','1'])].copy()
v=read('cpe_db/cpe_version_details')
m=m.merge(v,on=['cve_id','criteria']).drop_duplicates()
m=m[m.version_text.notna()&m.version_text.ne('*')].copy()
m['decoded']=m.cve_id.map(decode)
# Resolve candidate infix boundaries using independently encoded repeated CVEs.
# Count each source key once, not each product/version configuration.
support=m[['cve_id','decoded']].drop_duplicates('cve_id').decoded.explode().value_counts()
def resolve(xs):
 if not xs:return []
 best=max(support[x] for x in xs)
 return [x for x in xs if support[x]==best]
m['candidates']=m.decoded
m['decoded']=m.decoded.map(resolve)
print('undecoded',m[m.decoded.map(len).eq(0)].cve_id.drop_duplicates().to_list())
print('ambiguous',m[m.decoded.map(len).gt(1)][['cve_id','decoded']].drop_duplicates('cve_id').to_string(index=False))
m[['cve_id','decoded']].drop_duplicates('cve_id').to_json('/workspace/work/decoding_audit.json',orient='records',indent=2)
# NVD detail URLs explicitly identify the KEV record without lossy noisy-key joins.
k=read('kev_db/kev_entries')
refs=k.notes.fillna('').str.findall(r'(?i)nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)').explode().dropna().str.upper()
print('KEV NVD refs',len(refs),'entries',len(k))
kev_ids=set(refs)
matched=m[m.decoded.map(lambda xs:bool(set(xs)&kev_ids))].copy()
matched['normalized_version']=matched.version_text.map(version)
print(matched[['decoded','version_text','normalized_version']].to_string(index=False))
assert m.decoded.map(len).eq(1).all(), 'Unresolved relevant CVE keys'
count=matched.normalized_version.nunique()
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(count)}))
print('Answer',count)
if __name__=='__main__':pass
