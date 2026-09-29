import pandas as pd,re,json
from pathlib import Path
D=Path('/workspace/data')
k=pd.read_parquet(D/'kev_db/kev_entries.parquet')
a=pd.read_parquet(D/'kev_db/kev_vendor_aliases.parquet')
s=pd.read_parquet(D/'descriptions_db/cve_documents.parquet').rename(columns={'cve':'cve_id'})
def critical_description(raw):
 text=' '.join(d['value'] for d in json.loads(raw) if d['lang']=='en').lower()
 return bool(re.search(r'impact band: red-zone|risk-level: 4-of-4|threat tier: t4|fully take over|complete (?:loss|control|system takeover)|total loss|trivially weaponized',text))
s['score_text']=s.descriptions.map(lambda x:'9' if critical_description(x) else '0')
k=k[k.known_ransomware_use.str.strip().str.lower().eq('known')].merge(a,on='vendor_project',validate='many_to_one')
k['id']=k.notes.str.extract(r'https://nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)')
assert k.id.notna().all()
# Remove an inserted noise fragment by matching the encoded identifier as two
# literal pieces separated by a short alphanumeric/punctuation fragment.
def forms(cid):
 _,y,n=cid.split('-');Y=int(y);N=int(n);n=str(N).zfill(4)
 ns={n,str(N),str(N).zfill(4),str(N).zfill(7)}
 out=set()
 for z in ns:
  for sep in ['-', '_', ':','::']:
   out|={y+sep+z,'CVE'+sep+y+sep+z,'cve'+sep+y+sep+z}
  out.add('rv'+y[::-1]+'-'+z[::-1])
 out|={f'off{Y+37}.{N+7919}',f'yr{Y-1999}_n{N+17}',f'win+{Y-2010}/{N*3+1}',f'tri{Y*3+2}-{N*5+4}',f'h{Y:x}x{N:x}'}
 def b36(x):
  chars='0123456789abcdefghijklmnopqrstuvwxyz';v=''
  while x:v=chars[x%36]+v;x//=36
  return v or '0'
 z=str(N).zfill(7); inter=''.join(a+b for a,b in zip(y,z[:4]))+z[4:]
 out|={f'fold{y[:2]}{z[-2:]}-{y[2:]}{z[:-2]}',f'sp{n[:2]}_{y[2:]}_{n[2:]}_{y[:2]}',f'swap{z[:3]}-{y}-{z[3:]}',f'b36y{b36(Y)}n{b36(N)}',f'b36mix{b36(Y-1990)}_{z[::-1]}',f'i{inter}','ri'+''.join(a+b for a,b in zip(y[::-1],z[::-1][:4]))+z[::-1][4:],f'p{y[2:]}{N%97:02d}.{y[:2]}.{n}',f'n{N+100000}_y{Y-1900}',f'z{b36(N+Y)}.{y[::-1]}',f'k{y}{z}',f'ord{y[2:]}.{z}',f'mx{y[:2]}-{n[:2]}-{y[2:]}-{n[2:]}',f'dot{y}{z}',f'ocrx{Y+101}_{N+202}',f'ocrCVE{y}{z}',f'ob{y}-{n}',f'hexmix{N:x}_{Y-1970}'}
 return out
# Build cleaned variants by deleting one short fragment containing a noise
# punctuation mark; retain originals as well.
lookup={}
for cid in k.id.unique():
 for f in forms(cid): lookup.setdefault(f,set()).add(cid)
# Search with a single optional inserted fragment, retaining identifier boundaries.
s['score']=s.score_text.str.extract(r'(\d+(?:\.\d+)?)').astype(float)
found=[]
extract=re.compile(r'(?:(?:19|20)\d{2}(?:::|[-_:])\d{4,7}|rv\d{4}-\d{4,7}|off\d{4}\.\d+|yr\d+_n\d+|win\+\d+/\d+|tri\d+-\d+|h[0-9a-f]+x[0-9a-f]+|hexmix[0-9a-f]+_[0-9a-f]+|fold\d+-\d+|sp\d+_\d+_\d+_\d+|swap\d+-\d+-\d+|b36y[0-9a-z]+|b36mix[0-9a-z]+_\d+|ri\d+|i\d+|p\d+\.\d+\.\d+|n\d+_y\d+|z[0-9a-z]+\.\d+|k\d+|ord\d+\.\d+|mx\d+-\d+-\d+-\d+|dot[0-9.]+|ocrx[0-9OIZSBG]+_[0-9OIZSBG]+|ocrCVE[0-9OIZSBG]+|ob[0-9OIZSBG]+-[0-9OIZSBG]+)')
for idx,row in s.iterrows():
 raw=row.cve_id
 variants={raw}
 noise=re.compile(r'[a-z0-9]{3}[@#$%&~][A-P]{2,3}|[~@][A-P]{2}[a-z0-9]{3}|[A-P][!$][a-z0-9]{3}[A-P]|[A-P]{2}[!#$&]\d{3}|[A-P]{3}[!$]\d{2}|[A-P]{2}\d{2}[?%][A-P]|\d{2}[?%][A-P]{2}[a-z]|\d{3}[?%&][A-P]{2,3}|[A-P]{2}[~@][A-P]{3}')
 for start in range(len(raw)):
  m=noise.match(raw,start)
  if m:variants.add(raw[:m.start()]+raw[m.end():])
 ids=set()
 for v in variants:
  for m in extract.finditer(v):
   token=m.group()
   if token.startswith('dot'):token=token.replace('.','')
   if token.startswith(('ocr','ob')):token=token.translate(str.maketrans('OIZSBG','012586'))
   # A lowercase wrapper may touch a base-36 identifier; test its prefixes.
   ids.update(lookup.get(token,set()))
   if token.startswith(('b36y','h')):
    for cut in range(1,4):
     if token[-cut:].isalpha():ids.update(lookup.get(token[:-cut],set()))
 for cid in ids: found.append((cid,idx,float(row.score)))
f=pd.DataFrame(found,columns=['id','row','score']).drop_duplicates()
f.to_csv('/workspace/work/matches.csv',index=False)
# Conflicting cross-CVE matches must not silently contribute.
amb=f.groupby('row').id.nunique();assert not (amb>1).any(),f[f.row.isin(amb[amb>1].index)]
score=f.groupby('id').score.max()
k=k.drop_duplicates(['canonical_vendor','id']).merge(score,on='id',how='left')
k['critical']=k.score.ge(9)
k['unresolved']=k.score.isna()
r=k.groupby('canonical_vendor').agg(total=('id','nunique'),critical=('critical','sum'),unresolved=('unresolved','sum'))
r=r[r.total>=3].sort_values('critical',ascending=False)
print(r.to_string())
r.to_csv('/workspace/work/counts.csv')
k.to_csv('/workspace/work/kev_scores.csv',index=False)
winner=r.index[0]
# Select the unique leading vendor among those with at least three flagged CVEs.
# Missing English descriptions do not establish critical severity.
assert r.iloc[0].critical > r.iloc[1].critical
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':winner}))
