import polars as pl,re,json
from pathlib import Path
D=Path('/workspace/data'); W=Path('/workspace/work')
def b36(n):
 s=''
 while n: n,r=divmod(n,36);s='0123456789abcdefghijklmnopqrstuvwxyz'[r]+s
 return s or '0'
def forms(c):
 _,ys,ns=c.split('-');y=int(ys);n=int(ns);ns=str(n).zfill(4);p=str(n).zfill(7)
 a=[f'CVE-{ys}-{ns}',f'cve-{ys}-{ns}',f'CVE_{ys}_{ns}',f'cve:{ys}:{ns}',f'{ys}-{ns}',f'{ys}_{ns}',f'{ys}:{ns}',f'{ys}::{ns}',f'k{ys}{p}',f'ord{y-2000:02d}.{p}',f'rv{ys[::-1]}-{ns[::-1]}',f'off{y+37}.{n+7919}',f'tri{y*3+2}-{n*5+4}',f'win+{y-2010}/{n*3+1}',f'yr{y-1999}_n{n+17}',f'n{n+100000}_y{y-1900}',f'b36y{b36(y)}n{b36(n)}',f'h{y:x}x{n:x}',f'hexmix{n:x}_{y-1970}',f'b36mix{b36(y-1990)}_{p[::-1]}',f'fold{ys[:2]}{ns[-2:]}-{ys[2:]}{p[:-2]}',f'swap{p[:3]}-{ys}-{p[3:]}',f'mx{ys[:2]}-{ns[:2]}-{ys[2:]}-{ns[2:]}',f'sp{ns[:2]}_{ys[2:]}_{ns[2:]}_{ys[:2]}',f'p{ys[2:]}{n%97:02d}.{ys[:2]}.{n}','i'+''.join(a+b for a,b in zip(ys,p))+p[4:],'ri'+''.join(a+b for a,b in zip(ys[::-1],p[::-1]))+p[::-1][4:],f'z{b36(n+y)}.{ys[::-1]}',f'dot{ys}{p}']
 tr=str.maketrans('012568','OIZSGB')
 a += ['ob'+f'{ys}-{ns}'.translate(tr),'ocrCVE'+(ys+p).translate(tr),'ocrx'+f'{y+101}_{n+202}'.translate(tr)]
 return a
kev=pl.read_parquet(D/'kev_db/kev_entries.parquet')
# NVD detail links explicitly identify each catalog record.
kev=kev.with_columns(pl.col('notes').str.extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)',1).alias('cve'))
assert kev['cve'].null_count()==0
lookup={}
for c in kev['cve'].unique():
 for f in forms(c): lookup.setdefault(f.translate(str.maketrans('OIZSGB','012568')).replace('.',''),set()).add(c)
trie={}
for f,cs in lookup.items():
 t=trie
 for ch in f:t=t.setdefault(ch,{})
 t['$']=cs

def resolve(s):
 out=set(); longest=0
 candidates=[]
 for size in [6,7]:
  for i in range(len(s)-size+1):
   cut=s[i:i+size]
   if re.fullmatch(r'(?:[A-P]{2}[!@#$%&?~][0-9]{3}|[A-P]{3}[!@#$%&?~][0-9]{2}|[a-z0-9]{3}[!@#$%&?~][A-P]{2,3}|[a-z0-9]{2}[!@#$%&?~][A-P]{3}|[0-9]{2}[!@#$%&?~][A-P]{2}[a-z0-9]|[A-P]{2}[0-9]{2}[!@#$%&?~][A-P]|[A-P][!@#$%&?~][a-z0-9]{3}[A-P]|[!@#$%&?~][A-P]{2}[a-z0-9]{3}|[A-P]{2}[!@#$%&?~][A-P]{3})',cut):candidates.append(s[:i]+s[i+size:])
 for s in candidates:
  s=s.translate(str.maketrans('OIZSGB','012568')).replace('.','')
  for i,ch in enumerate(s):
   if ch not in trie:continue
   t=trie
   for j in range(i,len(s)):
    t=t.get(s[j])
    if t is None:break
    if '$' in t and (j+1==len(s) or not s[j+1].isdigit()):
     length=j-i+1
     if length>longest:out=set(t['$']);longest=length
     elif length==longest:out.update(t['$'])
 return sorted(out)
if __name__=='__main__':
 check=kev.with_columns(pl.col('cve_ref').map_elements(resolve,return_dtype=pl.List(pl.String)).alias('decoded'))
 bad=check.filter(~pl.col('decoded').list.contains(pl.col('cve')))
 print('Unresolved KEV',bad.height)
 bad.select('cve_ref','cve').write_json(W/'unresolved.json')
 print(bad.select('cve_ref','cve').head(30).to_dicts())
 aliases=pl.read_parquet(D/'cpe_db/vendor_aliases.parquet').filter(pl.col('canonical_vendor')=='microsoft')['alias'].to_list()
 cpe=pl.read_parquet(D/'cpe_db/cpe_matches.parquet').with_columns(pl.coalesce(pl.col('criteria').str.extract(r'^cpe:2\.3:[^:]+:([^:]+):',1),pl.col('criteria').str.extract(r'^([^/\s]+)',1)).alias('alias'))
 cpe=cpe.filter(pl.col('alias').is_in(aliases)&pl.col('vulnerable_flag').str.to_lowercase().str.strip_chars().is_in(['true','t','1','yes','y','v','affected','vulnerable']))
 cpe=cpe.select('cve_id').unique().with_columns(pl.col('cve_id').map_elements(resolve,return_dtype=pl.List(pl.String)).alias('decoded'))
 scores=pl.read_parquet(D/'vulns_db/cvss_metadata.parquet').with_columns(pl.col('score_text').str.extract(r'(\d+(?:\.\d+)?)',1).cast(pl.Float64).alias('score')).filter(pl.col('score')>=7)
 scores=scores.with_columns(pl.col('cve_id').map_elements(resolve,return_dtype=pl.List(pl.String)).alias('decoded'))
 for name,df in [('kev',check),('cpe',cpe),('scores',scores)]:
  amb=df.filter(pl.col('decoded').list.len()>1)
  print(name,'rows',df.height,'matched',df.filter(pl.col('decoded').list.len()>0).height,'ambiguous',amb.height)
  amb.write_json(W/(name+'_ambiguous.json'))
 matches=cpe.select(pl.col('decoded').explode().alias('cve')).drop_nulls().unique().join(scores.select(pl.col('decoded').explode().alias('cve')).drop_nulls().unique(),on='cve',how='inner').join(kev.select('cve').unique(),on='cve',how='inner').sort('cve')
 unambiguous=cpe.filter(pl.col('decoded').list.len()==1).select(pl.col('decoded').explode().alias('cve')).drop_nulls().unique()
 assert matches.join(unambiguous,on='cve',how='anti').height==0, 'Result depends on an ambiguous configuration key'
 assert bad.height==0
 assert check.filter(pl.col('decoded').list.len()!=1).height==0
 assert scores.filter(pl.col('decoded').list.len()>1).height==0
 matches.write_csv(W/'matched_cves.csv')
 answer=str(matches.height)
 (W/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
 print('Answer:',answer)
