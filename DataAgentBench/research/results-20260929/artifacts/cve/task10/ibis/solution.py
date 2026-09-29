import json
from pathlib import Path
import ibis
import re
NOISE=[r'[A-P]{2}\d{2}[%?][A-P]',r'[A-P]{2}[#@$&~!](?:\d{3}|[A-P]{3})',r'[A-P]{3}[!$]\d{2}',r'[@~][A-P]{2}[a-z0-9]{3}',r'[a-z0-9]{3}[#&~][A-P]{3}',r'[a-z0-9]{3}[#&~][A-P]{2}',r'[A-P][!$][a-z0-9]{3}[A-P]',r'\d{3}[%?][A-P]{3}',r'\d{2}[%?][A-P]{2}[a-z0-9]']
def cleaned(raw):
 out=[]
 for p in NOISE:
  for m in re.finditer(p,raw):out.append(raw[:m.start()]+raw[m.end():])
 return out or [raw]
NOISE.append(r'[a-z0-9]{3}[@][A-P]{2}')
OCR=str.maketrans('OIZSBG','012586')
def decode_one(s):
 s=re.sub(r'[a-p]{3}(?=(?:::|=>|--|~~|__|[|#~$%/@])(?:(?:aux|end|via)=)?(?:trail|trace|frag|slot|node|leaf|tag|mark|note|cache|src|sink|seen|batch|edge|tail)-)', '', s)
 out=set()
 def add(y,n):
  try:
   y,n=int(y),int(n)
   if 1990<=y<=2030 and 0<n<10000000:out.add(f'CVE-{y}-{n:04d}')
  except (ValueError,TypeError):pass
 def matches(p):return re.finditer(p,s)
 for m in matches(r'(?:CVE[-_:]|cve[-_:])?(\d{4})[-_:]{1,2}(\d{4,7})'):add(*m.groups())
 for m in matches(r'off(\d{4})\.(\d+)'):add(int(m[1])-37,int(m[2])-7919)
 for m in matches(r'win\+(\d+)/(\d+)'):
  if (int(m[2])-1)%3==0:add(2010+int(m[1]),(int(m[2])-1)//3)
 for m in matches(r'tri(\d+)-(\d+)'):
  if (int(m[1])-2)%3==0 and (int(m[2])-4)%5==0:add((int(m[1])-2)//3,(int(m[2])-4)//5)
 for m in matches(r'yr(\d+)_n(\d+)'):add(1999+int(m[1]),int(m[2])-17)
 for m in matches(r'n(\d+)_y(\d+)'):add(1900+int(m[2]),int(m[1])-100000)
 for m in matches(r'ord(\d{2})\.(\d{7})'):add(2000+int(m[1]),m[2])
 for m in matches(r'p(\d{2})\d{2}\.(\d{2})\.(\d+)'):add(m[2]+m[1],m[3])
 for m in matches(r'rv(\d{4})-(\d+)'):add(m[1][::-1],m[2][::-1])
 for m in matches(r'swap(\d{3})-(\d{4})-(\d{4})'):add(m[2],m[1]+m[3])
 for m in matches(r'sp(\d+)_(\d{2})_(\d+)_(\d{2})'):add(m[4]+m[2],m[1]+m[3])
 for m in matches(r'mx(\d{2})-(\d+)-(\d{2})-(\d+)'):add(m[1]+m[3],m[2]+m[4])
 for m in matches(r'fold(\d{2})(\d{2})-(\d{2})(\d{5})'):add(m[1]+m[3],m[4]+m[2])
 for m in matches(r'ocrx([0-9OIZSBG]+)_([0-9OIZSBG]+)'):add(int(m[1].translate(OCR))-101,int(m[2].translate(OCR))-202)
 for m in matches(r'ob([0-9OIZSBG]{4})-([0-9OIZSBG]+)'):add(m[1].translate(OCR),m[2].translate(OCR))
 for m in matches(r'ocrCVE([0-9OIZSBG]{4})([0-9OIZSBG]{7})'):add(m[1].translate(OCR),m[2].translate(OCR))
 for m in matches(r'dot([\d.]+)'):
  d=m[1].replace('.','');add(d[:4],d[4:])
 for m in matches(r'(?:k)(\d{11})'):add(m[1][:4],m[1][4:])
 for m in matches(r'(ri|i)(\d{11})'):
  d=m[2]; y,n=d[:8:2],d[1:8:2]+d[8:];add(y[::-1] if m[1]=='ri' else y,n[::-1] if m[1]=='ri' else n)
 # Base encodings may have an unseparated three-letter wrapper suffix.
 for m in matches(r'h([0-9a-f]+)x([0-9a-f]+)'):
  for n in [m[2],m[2][:-3]]:
   if n:add(int(m[1],16),int(n,16))
 for m in matches(r'z([0-9a-z]+)\.(\d{4})'):
  add(m[2][::-1],int(m[1],36)-int(m[2][::-1]))
 for m in matches(r'b36y([0-9a-z]{3})n([0-9a-z]+)'):
  for n in [m[2],m[2][:-3]]:
   if n:add(int(m[1],36),int(n,36))
 for m in matches(r'b36mix([0-9a-z]+)_(\d{7})'):add(1990+int(m[1],36),m[2][::-1])
 for m in matches(r'hexmix([0-9a-f]+)_(\d+)'):
  for yy in [m[2],m[2][:-3]]:
   if yy:add(1970+int(yy),int(m[1],16))
 return out

def normalize(raw):
 return sorted(set().union(*(decode_one(s) for s in cleaned(raw)))) if raw else []


ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()

@ibis.udf.scalar.python
def cve_candidates(value: str) -> list[str]:
    return normalize(value)

kev = con.read_parquet(ROOT / 'kev_db/kev_entries.parquet')
aliases = con.read_parquet(ROOT / 'kev_db/kev_vendor_aliases.parquet')
scores = con.read_parquet(ROOT / 'vulns_db/cvss_metadata.parquet')

# The KEV notes retain the canonical CVE in the NVD URL. Check that it is
# recovered from the noisy key, and use it to disambiguate the key candidates.
kev = kev.mutate(
    cve=kev.notes.re_extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d{4,7})', 1),
    candidates=cve_candidates(kev.cve_ref),
)
assert kev.filter((kev.cve == '') | kev.cve.isnull() | ~kev.candidates.contains(kev.cve)).count().execute() == 0
ms = kev.join(aliases, 'vendor_project').filter(aliases.canonical_vendor == 'microsoft').select('cve', 'products_csv')
scores = scores.mutate(
    score=scores.score_text.re_extract(r'([0-9]+(?:\.[0-9]+)?)', 1).try_cast('decimal(10,4)'),
    candidates=cve_candidates(scores.cve_id),
)
assert scores.filter(scores.candidates.length() == 0).count().execute() == 0
scores = scores.mutate(cve=scores.candidates.unnest())
matched = ms.join(scores, 'cve')
qualified = matched.filter(matched.score >= 9)
products = qualified.select(product=qualified.products_csv.split(',').unnest())
products = products.mutate(product=products.product.strip().lower())
products = products.filter(products.product.notnull() & (products.product != '')).distinct().order_by('product')
count = int(products.count().execute())
products.to_parquet(OUT / 'qualifying_products.parquet')
matched.select('cve','products_csv','cve_id','score_text','score','candidates').to_parquet(OUT / 'matched_audit.parquet')
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{count} distinct products.'}) + '\n')
print('Count:', count)
print(products.to_pyarrow().to_pylist())
print('Microsoft KEV rows:', ms.count().execute())
print('Matched Microsoft CVEs:', matched.select('cve').distinct().count().execute())

