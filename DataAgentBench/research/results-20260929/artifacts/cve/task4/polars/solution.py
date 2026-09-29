import re,json
from pathlib import Path
from functools import lru_cache
import polars as pl
ROOT=Path('/workspace/data')
noise_patterns=[r'[A-P]{2}\d{2}[%?][A-P]',r'\d{2}[%?][A-P]{2}[a-z0-9]',r'[A-P][!$][a-z0-9]{3}[A-P]',r'[A-P]{2}[@~][A-P]{3}',r'[a-z0-9]{3}[&#@~][A-P]{3}',r'[A-P]{3}[!$]\d{2}',r'[A-P]{2}[!$&#]\d{3}',r'[a-z0-9]{3}[&#@~][A-P]{2}',r'[@~][A-P]{2}[a-z0-9]{3}',r'\d{3}[%?][A-P]{3}',r'\d{3}[%?][A-P]{2}']
noise_patterns=[re.compile(p) for p in noise_patterns]
def variants(s):
 return list(dict.fromkeys(s[:m.start()]+s[m.end():] for p in noise_patterns for m in p.finditer(s)))
ocr=str.maketrans('OIZSBG','012586')
# Return encoding name and its components; retain only complete payloads.
patts=[('normal',r'(?:(?i:CVE)[-_:])?(20\d{2})[-_:]{1,2}(\d+)'),('k',r'k(20\d{2})(\d{7})'),('i',r'i(\d{11})'),('ri',r'ri(\d{11})'),('yr',r'yr(\d{2})_n(\d+)'),('n',r'n(\d+)_y(\d{3})'),('rv',r'rv(\d{4})-(\d+)'),('ob',r'ob([0-9OIZSBG]{4})-([0-9OIZSBG]+)'),('ocr',r'ocrCVE([0-9OIZSBG]{4})([0-9OIZSBG]{7})'),('ocrx',r'ocrx([0-9OIZSBG]{4})_([0-9OIZSBG]+)'),('h',r'h([0-9a-f]{3})x([0-9a-f]+)'),('z',r'z([0-9a-z]+)\.(\d{4})'),('b36y',r'b36y([0-9a-z]{3})n([0-9a-z]+)'),('hexmix',r'hexmix([0-9a-f]+)_(\d+)'),('b36mix',r'b36mix([0-9a-z]+)_(\d+)'),('ord',r'ord(\d{2})\.(\d{7})'),('dot',r'dot([\d.]+)'),('swap',r'swap(\d+)-(\d{4})-(\d+)'),('sp',r'sp(\d+)_(\d{2})_(\d+)_(\d{2})'),('mx',r'mx(\d{2})-(\d+)-(\d{2})-(\d+)'),('p',r'p(\d+)\.(\d{2})\.(\d+)'),('off',r'off(\d{4})\.(\d+)'),('win',r'win\+(\d+)/(\d+)'),('fold',r'fold(\d{4})-(\d+)'),('tri',r'tri(\d{4})-(\d+)')]
patts=[(n,re.compile(p+r'$',0)) for n,p in patts]
def parts(s):
 # Strip the outer provenance suffix and the reversible three-letter wrapper.
 s=re.sub(r'(?:::(?:end|aux|via)=|[^a-z0-9]+)[a-z]+-[a-p]{4}$','',s)
 if re.search(r':(?:key|id|ctx|doc|slot|raw|join)[a-p]{3}$',s):
  s=re.sub(r':(?:key|id|ctx|doc|slot|raw|join)[a-p]{3}$','',s)
 elif re.search(r'[a-p]{3}$',s):s=s[:-3]
 s=s.rstrip(')]}>')
 matches=[(n,m) for n,p in patts for m in p.finditer(s)]
 if not matches:return
 longest=max(len(m.group()) for n,m in matches)
 for n,m in matches:
  if len(m.group())==longest:
   # prevent normal matches from being pieces of other numeric encodings
   if n=='normal' and m.start()>0 and s[m.start()-1].isdigit():continue
   yield n,m.groups()
def basic(n,g):
 if n=='normal':y,v=map(int,g)
 elif n in ('ob','ocr'):y,v=[int(x.translate(ocr)) for x in g]
 elif n=='ocrx':y,v=[int(x.translate(ocr)) for x in g];y-=101;v-=202
 elif n in ('k','ord'):y,v=map(int,g);y=y+2000 if n=='ord' else y
 elif n=='yr':y,v=map(int,g);y+=1999;v-=17
 elif n=='rv':y,v=[int(x[::-1]) for x in g]
 elif n=='h':y,v=[int(x,16) for x in g]
 elif n=='z':y=int(g[1][::-1]);v=int(g[0],36)-y
 elif n=='b36y':y,v=[int(x,36) for x in g]
 elif n=='dot':
  digits=g[0].replace('.','')
  if len(digits)!=11:return None
  y=int(digits[:4]);v=int(digits[4:])
 elif n=='swap':y=int(g[1]);v=int(g[0]+g[2])
 elif n=='sp':y=int(g[3]+g[1]);v=int(g[0]+g[2])
 elif n=='mx':y=int(g[0]+g[2]);v=int(g[1]+g[3])
 elif n=='p':y=int(g[1]+g[0][:2]);v=int(g[2])
 elif n=='n':y=int(g[1])+1900;v=int(g[0])-100000
 elif n=='off':y=int(g[0])-37;v=int(g[1])-7919
 elif n=='win':y=int(g[0])+2010;v=(int(g[1])-1)//3
 elif n=='tri':y=(int(g[0])-2)//3;v=(int(g[1])-4)//5
 elif n=='hexmix':y=int(g[1])+1970;v=int(g[0],16)
 elif n=='b36mix':y=int(g[0],36)+1990;v=int(g[1][::-1])
 elif n=='fold':
  if len(g[1])!=7:return None
  y=int(g[1][:2])+2000;v=int(g[1][2:])*100+int(g[0])-2000
 elif n in ('i','ri'):
  t=g[0];ys=t[:8:2];vs=t[1:8:2]+t[8:]
  y=int(ys[::-1] if n=='ri' else ys);v=int(vs[::-1] if n=='ri' else vs)
 else:return None
 return (y,v) if 1999<=y<=2030 and 0<v<10000000 else None
if __name__=='__main__':
 tables=[('cpe',ROOT/'cpe_db/cpe_matches.parquet','cve_id'),('cves',ROOT/'vulns_db/cves.parquet','cve_id'),('kev',ROOT/'kev_db/kev_entries.parquet','cve_ref'),('scores',ROOT/'vulns_db/cvss_metadata.parquet','cve_id')]
 rows=[]
 for t,p,c in tables:
  for s in pl.read_parquet(p)[c].unique():
   candidates=[(n,g,basic(n,g)) for v in variants(s) for n,g in parts(v)]
   rows.append({'table':t,'raw':s,'candidates':candidates})
 Path('/workspace/work/decoded_parts.json').write_text(json.dumps(rows))
 from collections import Counter
 print(Counter(n for r in rows for n,g,b in r['candidates']))
 print('missing',sum(not r['candidates'] for r in rows))
 for r in [r for r in rows if not r['candidates']][:30]:print(r['raw'],variants(r['raw']))
