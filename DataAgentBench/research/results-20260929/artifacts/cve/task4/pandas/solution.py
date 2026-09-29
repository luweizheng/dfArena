import re,json
from pathlib import Path
from functools import lru_cache
from fractions import Fraction
import pandas as pd
ROOT=Path('/workspace/data')
# Each key has one inserted noise token. Enumerate overlapping token patterns
# because digits or OCR letters at an insertion boundary can be ambiguous.
NOISE=[r'[A-P]{2}\d{2}[!?%&][A-P]',r'[A-P]{2}[!&#$]\d{3}',r'\d{2}[?%][A-P]{2}[a-z0-9]',r'\d{3}[!?%&][A-P]{3}',r'[a-z0-9]{3}[@#&~][A-P]{2,3}',r'[@~][A-P]{2}[a-z0-9]{3}',r'[A-P]{2}[@~][A-P]{3}',r'[A-P][!$][a-z0-9]{3}[A-P]',r'[A-P]{3}[!$]\d{2}']
NOISE=[re.compile('(?=('+q+'))') for p in NOISE for q in ([p.replace('{2,3}','{2}'),p.replace('{2,3}','{3}')] if '{2,3}' in p else [p])]
OCR=str.maketrans('OIZSBG','012586')
def variants(s):
 for p in NOISE:
  for m in p.finditer(s):yield s[:m.start()]+s[m.start()+len(m[1]):]

def inter(s,reverse=False):
 y=s[:8:2]; n=s[1:8:2]+s[8:]
 if reverse:y,n=y[::-1],n[::-1]
 return int(y),int(n)
SPECS=[
 (r'(?:CVE[-_:])?((?:19|20)\d{2})[-_:]{1,2}(\d{4,})',lambda a,b:(int(a),int(b))),
 (r'k(\d{4})(\d{7})',lambda a,b:(int(a),int(b))),
 (r'ocrCVE([0-9OIZSBG]{4})([0-9OIZSBG]{7})',lambda a,b:(int(a.translate(OCR)),int(b.translate(OCR)))),
 (r'ob([0-9OIZSBG]{4})-([0-9OIZSBG]{4,})',lambda a,b:(int(a.translate(OCR)),int(b.translate(OCR)))),
 (r'ocrx([0-9OIZSBG]{4})_([0-9OIZSBG]+)',lambda a,b:(int(a.translate(OCR))-101,int(b.translate(OCR))-202)),
 (r'off(\d{4})\.(\d+)',lambda a,b:(int(a)-37,int(b)-7919)),
 (r'tri(\d{4})-(\d+)',lambda a,b:((int(a)-2)//3,(int(b)-4)//5) if (int(a)-2)%3==0 and (int(b)-4)%5==0 else (0,0)),
 (r'win\+(\d+)/(\d+)',lambda a,b:(2010+int(a),(int(b)-1)//3) if (int(b)-1)%3==0 else (0,0)),
 (r'yr(\d+)_n(\d+)',lambda a,b:(1999+int(a),int(b)-17)),
 (r'n(\d+)_y(\d+)',lambda a,b:(1900+int(b),int(a)-100000)),
 (r'ord(\d{2})\.(\d{7})',lambda a,b:(2000+int(a),int(b))),
 (r'rv(\d{4})-(\d+)',lambda a,b:(int(a[::-1]),int(b[::-1]))),
 (r'swap(\d{3})-(\d{4})-(\d{4})',lambda a,b,c:(int(b),int(a+c))),
 (r'fold(\d{4})-(\d{7})',lambda a,b:(int(a[:2]+b[:2]),int(b[2:]+a[2:]))),
 (r'p(\d{4})\.(\d{2})\.(\d+)',lambda a,b,c:(int(b+a[:2]),int(c))),
 (r'sp(\d{2})_(\d{2})_(\d+)_(\d{2})',lambda a,b,c,d:(int(d+b),int(a+c))),
 (r'mx(\d{2})-(\d{2})-(\d{2})-(\d+)',lambda a,b,c,d:(int(a+c),int(b+d))),
 (r'dot([\d.]+)',lambda a:(int(a.replace('.','')[:4]),int(a.replace('.','')[4:])) if len(a.replace('.',''))==11 else (0,0)),
 (r'h([0-9a-f]{3})x([0-9a-f]+)',lambda a,b:(int(a,16),int(b,16))),
 (r'hexmix([0-9a-f]+)_(\d{2})',lambda a,b:(1970+int(b),int(a,16))),
 (r'b36y([0-9a-z]{3})n([0-9a-z]+)',lambda a,b:(int(a,36),int(b,36))),
 (r'b36mix([0-9a-z]+)_(\d{7})',lambda a,b:(1990+int(a,36),int(b[::-1]))),
 (r'z([0-9a-z]+)\.(\d{4})',lambda a,b:(int(b[::-1]),int(a,36)-int(b[::-1]))),
 (r'ri(\d{11})',lambda a:inter(a,True)),
 (r'i(\d{11})',lambda a:inter(a)),
]
END=r'(?=[a-p]{3}(?:[^a-z0-9]|$)|[^a-zA-Z0-9]|$)'
SPECS=[(re.compile(p+END),f) for p,f in SPECS]
def decode(s,allowed):
 found=set()
 for v in variants(s):
  for p,f in SPECS:
   vv=re.sub(r'[a-p]{3}(?=::|--|__|=>|[~@#$%/|]|\+\+)', '',v) if p.pattern.startswith(('h(', 'b36y')) else v
   for m in p.finditer(vv):
    if p is SPECS[0][0] and re.search(r'(?:swap|fold|rv\d|tri\d|off\d|mx\d)',vv[:m.start()]):continue
    try:
     y,n=f(*m.groups()); key=f'CVE-{y:04d}-{n:04d}'
     if key in allowed:found.add(key)
    except ValueError:pass
 return found

def main():
 kev=pd.read_parquet(ROOT/'kev_db/kev_entries.parquet')
 refs=kev.notes.fillna('').map(lambda s:set(x.upper() for x in re.findall(r'CVE-\d{4}-\d{4,}',s,re.I)))
 universe=set().union(*refs)
 ksets=[decode(s,ids) for s,ids in zip(kev.cve_ref,refs)]
 bad=[(s,sorted(ids),sorted(got)) for s,ids,got in zip(kev.cve_ref,refs,ksets) if len(got)!=1]
 print('KEV unresolved',len(bad),flush=True)
 for b in bad[:35]:print(b,flush=True)
 assert not bad, 'Unresolved KEV identifiers'
 kev['cve']= [next(iter(x)) for x in ksets]
 targets=set(kev.cve)
 cpe=pd.read_parquet(ROOT/'cpe_db/cpe_matches.parquet')
 scores=pd.read_parquet(ROOT/'vulns_db/cvss_metadata.parquet')
 keys=pd.unique(pd.concat([cpe.cve_id,scores.cve_id],ignore_index=True))
 mapping={}; ambiguous=[]
 for i,s in enumerate(keys):
  ids=decode(s,targets)
  if len(ids)==1:mapping[s]=next(iter(ids))
  elif len(ids)>1:ambiguous.append((s,ids))
 print('mapped',len(mapping),'ambiguous',ambiguous[:10],flush=True)
 assert not ambiguous
 cpe['cve']=cpe.cve_id.map(mapping)
 truth={'t','y','yes','affected','vulnerable','v','true','1'}
 vulnerable=set(cpe.loc[cpe.vulnerable_flag.str.strip().str.lower().isin(truth),'cve'].dropna())
 scores['cve']=scores.cve_id.map(mapping)
 scores['score']=pd.to_numeric(scores.score_text.str.extract(r'(\d+(?:\.\d+)?)',expand=False))
 scores=scores.dropna(subset=['cve'])
 assert scores.groupby('cve').score.nunique().max()==1
 scores.to_csv('/workspace/work/matched_scores.csv',index=False)
 score=scores.groupby('cve').score.first()
 aliases=pd.read_parquet(ROOT/'kev_db/kev_vendor_aliases.parquet')
 eligible=kev.merge(aliases,on='vendor_project',validate='many_to_one')
 eligible=eligible[eligible.cve.isin(vulnerable)].drop_duplicates(['canonical_vendor','cve'])
 print('Distinct KEV CVEs:',len(targets),'with vulnerable CPE:',eligible.cve.nunique(),'with score:',eligible.cve.isin(score.index).sum(),flush=True)
 eligible['high']=eligible.cve.map(score).ge(9)
 stats=eligible.groupby('canonical_vendor').agg(total=('cve','nunique'),high=('high','sum'))
 stats=stats[stats.total>=10].copy()
 stats['share']=[Fraction(int(h),int(n)) for h,n in zip(stats.high,stats.total)]
 stats=stats.reset_index().sort_values(['share','canonical_vendor'],ascending=[False,True])
 stats.to_csv('/workspace/work/vendor_shares.csv',index=False)
 print(stats.to_string(index=False),flush=True)
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':stats.iloc[0].canonical_vendor})+'\n')
if __name__=='__main__':main()
