import pandas as pd
import re,json
from pathlib import Path
ROOT=Path('/workspace/data')
noise=re.compile(r'(?=([A-P]{2}\d{2}[?%][A-P]|\d{3}[?%][A-P]{3}|[A-P]{2}[!$&#]\d{3}|\d{2}[?%][A-P]{2}[a-z0-9]|[~@][A-P]{2}[a-z0-9]{3}|[a-z0-9]{3}[~#&@][A-P]{2,3}|[A-P][!$][a-z0-9]{3}[A-P]|[A-P]{3}[!$]\d{2}|[A-P]{2}[&@~#][A-P]{3}))')
def variants(s):
 for m in noise.finditer(s):
  yield s[:m.start()]+s[m.start()+len(m[1]):]
  if re.fullmatch(r'[a-z0-9]{3}[~#&@][A-P]{3}',m[1]): yield s[:m.start()]+s[m.start()+len(m[1])-1:]
def core(s):
 s=re.sub(r'^[a-z]+-[a-p]{5}','',s)
 s=re.sub(r'^(?:(?:::|=>|__|\+\+|~~|--|[~@/#%$|])|(?:ref|id|key|raw|slot|join|doc|ctx)[:=]|[<({\[])*[a-p]{3}(?:::|[~@/#:|])?','',s)
 s=re.split(r':(?:join|slot|raw|ctx|key|doc|id)[a-p]{3}|(?<!=)[)}>\]][a-p]{3}',s)[0]
 s=re.sub(r'[a-p]{3}=>.*$','',s)
 s=re.sub(r'[a-p]{3}(?=::|=>|__|\+\+|~~|--|[~@/#%$|]).*$','',s)
 return s.rstrip("}")
OCR=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
def decode(t):
 y=n=None
 def match(p): return re.fullmatch(p,t)
 if m:=match(r'(?:CVE[-_:]|cve[-_:])?(\d{4})[-_:]{1,2}(\d+)'): y,n=map(int,m.groups())
 elif m:=match(r'k(\d{4})(\d{7})'): y,n=map(int,m.groups())
 elif m:=match(r'(i|ri)(\d{11})'):
  q=m[2];a=q[:8:2];b=q[1:8:2]+q[8:];y=int(a[::-1] if m[1]=='ri' else a);n=int(b[::-1] if m[1]=='ri' else b)
 elif m:=match(r'rv(\d{4})-(\d+)'): y=int(m[1][::-1]);n=int(m[2][::-1])
 elif m:=match(r'off(\d+)\.(\d+)'): y=int(m[1])-37;n=int(m[2])-7919
 elif m:=match(r'n(\d+)_y(\d+)'): y=int(m[2])+1900;n=int(m[1])-100000
 elif m:=match(r'yr(\d+)_n(\d+)'): y=int(m[1])+1999;n=int(m[2])-17
 elif m:=match(r'ord(\d+)\.(\d+)'): y=int(m[1])+2000;n=int(m[2])
 elif m:=match(r'win\+(\d+)/(\d+)'): y=int(m[1])+2010;n=(int(m[2])-1)/3
 elif m:=match(r'tri(\d+)-(\d+)'): y=(int(m[1])-2)/3;n=(int(m[2])-4)/5
 elif m:=match(r'h([0-9a-f]+)x([0-9a-f]+)'): y=int(m[1],16);n=int(m[2],16)
 elif m:=match(r'z([0-9a-z]+)\.(\d{4})'): y=int(m[2][::-1]);n=int(m[1],36)-y
 elif m:=match(r'b36mix([0-9a-z]+)_(\d{7})'): y=int(m[1],36)+1990;n=int(m[2][::-1])
 elif m:=match(r'hexmix([0-9a-f]+)_([0-9a-f]+)'): y=int(m[2])+1970;n=int(m[1],16)
 elif m:=match(r'b36y([0-9a-z]{3})n([0-9a-z]+)'): y=int(m[1],36);n=int(m[2],36)
 elif m:=match(r'swap(\d{3})-(\d{4})-(\d{4})'): y=int(m[2]);n=int(m[1]+m[3])
 elif m:=match(r'fold(\d{2})(\d{2})-(\d{2})(\d{5})'): y=int(m[1]+m[3]);n=int(m[4]+m[2])
 elif m:=match(r'p(\d{2})\d{2}\.(\d{2})\.(\d+)'): y=int(m[2]+m[1]);n=int(m[3])
 elif m:=match(r'mx(\d{2})-(\d+)-(\d{2})-(\d+)'): y=int(m[1]+m[3]);n=int(m[2]+m[4])
 elif m:=match(r'sp(\d+)_(\d{2})_(\d+)_(\d{2})'): y=int(m[4]+m[2]);n=int(m[1]+m[3])
 elif t.startswith('dot'):
  q=t[3:].replace('.','')
  if q.isdigit() and len(q)==11: y=int(q[:4]);n=int(q[4:])
 elif m:=match(r'ob([0-9OIZSGB]{4})-([0-9OIZSGB]+)'): y=int(m[1].translate(OCR));n=int(m[2].translate(OCR))
 elif m:=match(r'ocrx([0-9OIZSGB]+)_([0-9OIZSGB]+)'): y=int(m[1].translate(OCR))-101;n=int(m[2].translate(OCR))-202
 elif m:=match(r'ocrCVE([0-9OIZSGB]{11})'): q=m[1].translate(OCR);y=int(q[:4]);n=int(q[4:])
 if y is not None and 1990<=y<=2030 and n>0 and y==int(y) and n==int(n): return f'CVE-{int(y)}-{int(n):04d}'
def normalize(s): return {v for t in variants(s) if (v:=decode(core(t)))}
def main():
 scores=pd.read_parquet(ROOT/'vulns_db/cvss_metadata.parquet')
 kev=pd.read_parquet(ROOT/'kev_db/kev_entries.parquet')
 aliases=pd.read_parquet(ROOT/'kev_db/kev_vendor_aliases.parquet')
 kev=kev.merge(aliases,on='vendor_project',validate='many_to_one').query('canonical_vendor == "microsoft"').copy()
 scores['ids']=scores.cve_id.map(normalize)
 kev['ids']=kev.cve_ref.map(normalize)
 # Validate decoded KEV identifiers against the catalog's own CVE URLs.
 for idx,r in kev.iterrows():
  note_ids=set(re.findall(r'CVE-\d{4}-\d{4,}',r.notes or ''))
  confirmed=r.ids & note_ids
  assert len(confirmed)==1, (r.cve_ref, confirmed)
  kev.at[idx,'ids']=confirmed
 assert scores.ids.map(bool).all(), 'Unresolved score identifiers'
 scores['score']=pd.to_numeric(scores.score_text.str.extract(r'(\d+(?:\.\d+)?)',expand=False))
 microsoft_ids=set().union(*kev.ids)
 critical=scores[scores.score>=9]
 relevant=critical[critical.ids.map(lambda ids:bool(ids & microsoft_ids))]
 assert relevant.ids.map(len).eq(1).all(), 'Ambiguous qualifying score join'
 high=critical.explode('ids').dropna(subset=['ids'])
 qualifying=kev.explode('ids').merge(high[['ids']].drop_duplicates(),on='ids')
 products=qualifying.products_csv.str.split(',').explode().str.strip().str.casefold()
 products=products[products.ne('')].dropna().drop_duplicates().sort_values()
 products.to_csv('/workspace/work/qualifying_products.csv',index=False,header=['product'])
 print('Distinct qualifying products:',len(products))
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(len(products))})+'\n')
if __name__=='__main__': main()
