import pandas as pd, re, json
from pathlib import Path
ROOT=Path('/workspace/data')
OLD_PATTERNS=[r'[a-z0-9]{3}[~!@#$%&?][A-P]{3}',r'[a-z0-9]{3}[~!@#$%&?][A-P]{2}',r'[A-P]{2}[~!@#$%&?][0-9]{3}',r'[0-9]{3}[~!@#$%&?][A-P]{3}',r'[A-P]{3}[~!@#$%&?][0-9]{2}',r'[A-P]{2}[0-9]{2}[~!@#$%&?][A-P]',r'[A-P][~!@#$%&?][a-z0-9]{3}[A-P]',r'[~!@#$%&?][A-P]{2}[a-z0-9]{3}',r'[0-9]{2}[~!@#$%&?][A-P]{2}[a-z0-9]',r'[A-P]{2}[~!@#$%&?][A-P]{3}']
PATTERNS=OLD_PATTERNS
OCR=str.maketrans('OIZSBG','012586')
def parse(s):
 out=[]
 def add(y,n):
  y,n=int(y),int(n)
  if 1999<=y<=2035 and 1<=n<10000000:out.append((m.end()-m.start(),f'CVE-{y}-{n:04d}'))
 end=r'(?=$|[^a-zA-Z0-9]|[a-p]{3}(?:$|[^a-zA-Z0-9]))'
 forms=[
 (r'(?:CVE-|cve-|CVE_|cve:)?(20\d{2})[-_:]{1,2}(\d{4,7})',lambda a,b:(a,b)),
 (r'k(20\d{2})(\d{7})',lambda a,b:(a,b)),
 (r'yr(\d{1,2})_n(\d+)',lambda a,b:(2000+int(a)-1,int(b)-17)),
 (r'n(\d+)_y(\d+)',lambda a,b:(1900+int(b),int(a)-100000)),
 (r'off(\d{4})\.(\d+)',lambda a,b:(int(a)-37,int(b)-7919)),
 (r'win\+?(-?\d+)/(\d+)',lambda a,b:(2010+int(a),(int(b)-1)//3)),
 (r'tri(\d{4})-(\d+)',lambda a,b:((int(a)-2)//3,(int(b)-4)//5)),
 (r'rv(\d{4})-(\d+)',lambda a,b:(a[::-1],b[::-1])),
 (r'ord(\d{2})\.(\d{7})',lambda a,b:(2000+int(a),b)),
 (r'hexmix([0-9a-f]+)_(\d+)',lambda a,b:(1970+int(b),int(a,16))),
 (r'h([0-9a-f]{3})x([0-9a-f]{1,5})',lambda a,b:(int(a,16),int(b,16))),
 (r'b36mix([0-9a-z]+)_(\d{7})',lambda a,b:(1990+int(a,36),b[::-1])),
 (r'b36y([0-9a-z]{3})n([0-9a-z]+?)',lambda a,b:(int(a,36),int(b,36))),
 (r'z([0-9a-z]+?)\.(\d{4})',lambda a,b:(b[::-1],int(a,36)-int(b[::-1]))),
 (r'swap(\d{3})-(\d{4})-(\d{4})',lambda a,b,c:(b,a+c)),
 (r'mx(\d{2})-(\d+)-(\d{2})-(\d+)',lambda a,b,c,d:(a+c,b+d)),
 (r'sp(\d+)_(\d{2})_(\d+)_(\d{2})',lambda a,b,c,d:(d+b,a+c)),
 (r'p(\d{2})\d{2}\.(\d{2})\.(\d+)',lambda a,b,c:(b+a,c)),
 (r'fold(\d{4})-(\d{7})',lambda a,b:(2000+int(b[:2]),int(b[2:])*100+int(a)-2000)),
 (r'i(\d{11})',lambda a:(a[:8:2],a[1:8:2]+a[8:])),
 (r'ri(\d{11})',lambda a:(a[:8:2][::-1],(a[1:8:2]+a[8:])[::-1])),
 (r'dot([\d.]+\d)',lambda a:(''.join(a.split('.'))[:4],''.join(a.split('.'))[4:])),
 (r'ob([0-9OIZSBG]{4})-([0-9OIZSBG]+)',lambda a,b:(a.translate(OCR),b.translate(OCR))),
 (r'ocrCVE([0-9OIZSBG]{4})([0-9OIZSBG]{7})',lambda a,b:(a.translate(OCR),b.translate(OCR))),
 (r'ocrx([0-9OIZSBG]{4})_([0-9OIZSBG]+)',lambda a,b:(int(a.translate(OCR))-101,int(b.translate(OCR))-202)),
 ]
 for pat,fn in forms:
  for m in re.finditer(r'(?<![A-Z0-9_-])'+pat+end,s):
   try:add(*fn(*m.groups()))
   except ValueError:pass
 return {v for length,v in out if length==max((n for n,_ in out),default=0)}

def candidates(s):
 options=[]
 for p in PATTERNS:
  for m in re.finditer('(?=('+p+'))',s):
   token=m.group(1)
   t=s[:m.start()]+s[m.start()+len(token):]
   ids=parse(t)
   if ids: options.append((noise_counts.get(token,0),len(token),ids))
 if not options:return set()
 best=max((freq,length) for freq,length,ids in options)
 return set().union(*(ids for freq,length,ids in options if (freq,length)==best))

if __name__=='__main__':
 from collections import Counter
 d=pd.read_parquet(ROOT/'descriptions_db/cve_documents.parquet')
 k=pd.read_parquet(ROOT/'kev_db/kev_entries.parquet')
 noise_counts=Counter()
 for x in pd.concat([d.cve,k.cve_ref]):
  tokens=set()
  for p in PATTERNS:
   tokens.update(m[1] for m in re.finditer('(?=('+p+'))',x))
  noise_counts.update(tokens)
 d['ids']=d.cve.map(candidates);k['ids']=k.cve_ref.map(candidates)
 for name,df,col in [('docs',d,'cve'),('kev',k,'cve_ref')]:
  print(name,df.ids.map(len).value_counts().to_dict())
  df.loc[df.ids.map(len)!=1,[col,'ids']].to_csv('/workspace/work/'+name+'_unresolved.csv',index=False)
 d.to_pickle('/workspace/work/docs.pkl');k.to_pickle('/workspace/work/kev.pkl')

 assert d.ids.map(len).eq(1).all() and k.ids.map(len).eq(1).all()
 d['cve_id']=d.ids.map(lambda v:next(iter(v)))
 k['cve_id']=k.ids.map(lambda v:next(iter(v)))
 languages=d.descriptions.map(lambda value:json.loads(value) if pd.notna(value) else [])
 d['has_en']=languages.map(lambda items:any(item.get('lang','').lower()=='en' for item in items))
 d['has_non_en']=languages.map(lambda items:any(item.get('lang','').lower() not in ('','en') for item in items))
 flags=d.groupby('cve_id')[['has_en','has_non_en']].any()
 qualifying=flags.loc[~flags.has_en & flags.has_non_en].reset_index()
 matched=qualifying.merge(k[['cve_id']].drop_duplicates(),on='cve_id',how='inner')
 matched.to_csv('/workspace/work/matched_cves.csv',index=False)
 count=int(matched.cve_id.nunique())
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(count)})+'\n')
 print('Answer:',count)
