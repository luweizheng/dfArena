import pandas as pd, re, json
from pathlib import Path
ROOT=Path('/workspace/data')
k=pd.read_parquet(ROOT/'kev_db/kev_entries.parquet')
# The final NVD link in KEV notes supplies its unambiguous catalog identifier.
kev=set(k.notes.fillna('').str.findall(r'https://nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)').str[-1].dropna())
assert len(kev)==len(k)
# Generate reversible surface encodings for catalog identifiers.
def b36(n):
 s=''
 while n: n,r=divmod(n,36);s='0123456789abcdefghijklmnopqrstuvwxyz'[r]+s
 return s or '0'
enc={}
for c in kev:
 _,ys,ns=c.split('-'); y,n=int(ys),int(ns); z=f'{n:07d}'
 forms=[f'{y}-{ns}',f'{y}_{ns}',f'{y}:{ns}',f'{y}::{ns}',f'k{y}{z}',f"i{''.join(a+b for a,b in zip(str(y),z[:4]))+z[4:]}",f"ri{''.join(a+b for a,b in zip(str(y)[::-1],z[::-1][:4]))+z[::-1][4:]}",f'rv{str(y)[::-1]}-{ns[::-1]}',f'ord{y-2000:02d}.{z}',f'off{y+37}.{n+7919}',f'win+{y-2010}/{n*3+1}',f'tri{y*3+2}-{n*5+4}',f'yr{y-1999}_n{n+17}',f'n{n+100000}_y{y-1900}',f'b36y{b36(y)}n{b36(n)}',f'h{y:x}x{n:x}',f'hexmix{n:x}_{y-1970}',f'b36mix{b36(y-1990)}_{z[::-1]}',f'p{str(y)[2:]}{n%97:02d}.{str(y)[:2]}.{n}', f'z{b36(n+y)}.{str(y)[::-1]}', f'mx{str(y)[:2]}-{ns[:2]}-{str(y)[2:]}-{ns[2:]}',f'fold{str(y)[:2]}{z[-2:]}-{str(y)[2:]}{z[:-2]}',f'swap{z[:3]}-{y}-{z[3:]}',f'sp{ns[:2]}_{str(y)[2:]}_{ns[2:]}_{str(y)[:2]}']
 for f in forms: enc[f]=c
# Match other numeric encodings after stripping separators/OCR substitutions.
ocr=str.maketrans({'O':'0','Z':'2','I':'1','S':'5','G':'6','B':'8'})
patterns=re.compile(r'(?:z[0-9a-z]+\.\d{4}|mx\d+-\d+-\d+-\d+|b36mix[0-9a-z]+_\d+|b36y[0-9a-z]+n[0-9a-z]+|hexmix[0-9a-f]+_\d+|h[0-9a-f]+x[0-9a-f]+|(?:ord|off)\d+\.\d+|win\+\d+/\d+|tri\d+-\d+|yr\d+_n\d+|n\d+_y\d+|p\d+\.\d+\.\d+|fold\d+-\d+|swap\d+-\d+-\d+|sp\d+_\d+_\d+_\d+|rv\d+-\d+|ri\d+|[ki]\d{11}|20\d{2}(?:::|[-_:])\d{4,})')
def identify(s):
 out=set()
 # Noise is a six-character infix with a punctuation mark and capital letters.
 candidates=[s]
 for length in (6,7):
  for i in range(len(s)-length+1):
   t=s[i:i+length]
   if sum('A'<=x<='P' for x in t)>=2 and any(x in '~@&?!$#%' for x in t): candidates.append(s[:i]+s[i+length:])
 for a in candidates:
  for m in patterns.finditer(a):
   f=m.group();c=enc.get(f)
   if c: out.add(c)
   if not c and f.startswith(('b36y','h')) and len(f)>3:
    for trim in (1,2,3):
     c=enc.get(f[:-trim])
     if c:out.add(c)
  for m in re.finditer(r'(?:ocrCVE|ob|ocrx)([0-9OZISGB]+)[_-]?([0-9OZISGB]*)',a):
   v,w=[x.translate(ocr) for x in m.groups()]
   if a[m.start():].startswith('ocrCVE'): y,n=int(v[:4]),int(v[4:]) if len(v)>4 else 0
   elif not w: continue
   else: y,n=int(v),int(w)
   if a[m.start():].startswith('ocrx'): y-=101;n-=202
   c=f'CVE-{y}-{n:04d}'
   if c in kev:out.add(c)
  for m in re.finditer(r'dot([0-9.]+)',a):
   d=m.group(1).replace('.','')
   if len(d)==11:
    c=f'CVE-{d[:4]}-{int(d[4:]):04d}'
    if c in kev:out.add(c)
 return bool(out)
m=pd.read_parquet(ROOT/'cpe_db/cpe_matches.parquet')
m=m[m.vulnerable_flag.str.strip().str.lower().isin(['t','y','yes','affected','vulnerable','v','true','1'])].copy()
a=pd.read_parquet(ROOT/'cpe_db/vendor_aliases.parquet'); aliases=dict(zip(a.alias.str.lower(),a.canonical_vendor.str.lower()))
def product(s):
 if s.startswith('cpe:2.3:'): v,p=s.split(':')[3:5]
 elif '/' in s: v,p=s.split('/',1);p=p.rsplit('@',1)[0]
 else: v,p=s.split(' ',1);p=p.rsplit(' ',1)[0].lower().replace(' ','_')
 return aliases.get(v.lower(),v.lower())+':'+p.lower()
m['pair']=m.criteria.map(product)
u=m.cve_id.drop_duplicates(); flags={s:identify(s) for s in u}
m['kev']=m.cve_id.map(flags)
counts=m[m.kev].groupby('pair').size().sort_values(ascending=False)
print('Catalog IDs',len(kev),'Matched rows',m.kev.sum());print(counts.head(15))
counts.to_csv('/workspace/work/counts.csv')
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':counts.index[0]}))
