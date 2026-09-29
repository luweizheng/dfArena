"""Count distinct KEV CVEs with duplicate, conflicting registry attack vectors.

Only the supplied Parquet data is used. Identifier noise tokens are inferred
from unambiguous registry keys and verified KEV keys. Canonical KEV IDs are
available in each KEV row's NVD link. All potentially KEV-related registry
keys must resolve uniquely before aggregation.
"""
import json
from pathlib import Path
from collections import Counter
import pandas as pd
import re
P=re.compile(r'^[a-z]+-[a-p]{5}(?:::id=|::key=|::ref=|::|=>|~~|\+\+|--|__|[/%~@#$|])')
TAIL=re.compile(r'(?:::aux=|::via=|::end=|::|=>|~~|\+\+|--|__|[/%~@#$|])[a-z]+-[a-p]{4}$')
PRE=re.compile(r'^(?:(?:doc|id|key|raw|ctx|slot|join):)?[<({\[]?[a-p]{3}(?:::|[:/#@|~])?')
SUF=re.compile(r'(?::(?:doc|id|key|raw|ctx|slot|join)[a-p]{3}|[)>}\]][a-p]{3}|[a-p]{3})$')
def body(s):
 s=P.sub('',s);s=TAIL.sub('',s);s=PRE.sub('',s);s=SUF.sub('',s);return s
# Each noisy key contains one inserted token. Specific token shapes first.
NOISE=[r'[!@#$%&?~][A-P]{2}[a-z0-9]{3}',r'\d{2}[!@#$%&?~][A-P]{2}[a-z0-9]',r'[A-P]{3}[!@#$%&?~]\d{2}',r'[A-P]{2}\d{2}[!@#$%&?~][A-P]',r'[A-P][!@#$%&?~][a-z0-9]{3}[A-P]',r'[A-P]{2}[!@#$%&?~][A-P]{3}',r'[A-P]{2}[!@#$%&?~]\d{3}',r'[a-z0-9]{3}[!@#$%&?~][A-P]{2,3}']
def clean(s):
 for p in NOISE:
  if re.search(p,s):return re.sub(p,'',s,count=1)
 return s
TRANS=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
def parse(s):
 def m(p):return re.fullmatch(p,s)
 y=n=None
 if a:=m(r'(?:CVE[-_]|cve[-:])?(\d{4})[-_:]+(\d{4,7})'): y,n=a.groups()
 elif a:=m(r'k(\d{4})(\d{7})'): y,n=a.groups()
 elif a:=m(r'ord(\d{2})\.(\d{7})'):y,n=2000+int(a[1]),a[2]
 elif a:=m(r'yr(\d+)_n(\d+)'):y,n=1999+int(a[1]),int(a[2])-17
 elif a:=m(r'off(\d+)\.(\d+)'):y,n=int(a[1])-37,int(a[2])-7919
 elif a:=m(r'n(\d+)_y(\d+)'):y,n=1900+int(a[2]),int(a[1])-100000
 elif a:=m(r'win\+(\d+)/(\d+)'):
  if (int(a[2])-1)%3:return
  y,n=2010+int(a[1]),(int(a[2])-1)//3
 elif a:=m(r'tri(\d+)-(\d+)'):
  if (int(a[1])-2)%3 or (int(a[2])-4)%5:return
  y,n=(int(a[1])-2)//3,(int(a[2])-4)//5
 elif a:=m(r'p(\d{2})(\d{2})\.(\d{2})\.(\d+)'):
  y,n=a[3]+a[1],a[4]
  if int(n)%97!=int(a[2]):return
 elif a:=m(r'fold(\d{2})(\d{2})-(\d{2})(\d{5})'):y,n=a[1]+a[3],a[4]+a[2]
 elif a:=m(r'swap(\d{3})-(\d{4})-(\d{4})'):y,n=a[2],a[1]+a[3]
 elif a:=m(r'mx(\d{2})-(\d+)-(\d{2})-(\d+)'):y,n=a[1]+a[3],a[2]+a[4]
 elif a:=m(r'sp(\d+)_(\d{2})_(\d+)_(\d{2})'):y,n=a[4]+a[2],a[1]+a[3]
 elif a:=m(r'rv(\d{4})-(\d+)'):y,n=a[1][::-1],a[2][::-1]
 elif a:=m(r'(i|ri)(\d{11})'):
  z=a[2];y=z[:8:2];n=z[1:8:2]+z[8:]
  if a[1]=='ri':y,n=y[::-1],n[::-1]
 elif a:=m(r'dot([\d.]+)'):
  z=a[1].replace('.','')
  if len(z)!=11:return
  y,n=z[:4],z[4:]
 elif a:=m(r'h([0-9a-f]+)x([0-9a-f]+)'):y,n=int(a[1],16),int(a[2],16)
 elif a:=m(r'hexmix([0-9a-f]+)_(\d+)'):y,n=int(a[2])+1970,int(a[1],16)
 elif a:=m(r'b36y([0-9a-z]{3})n([0-9a-z]+)'):y,n=int(a[1],36),int(a[2],36)
 elif a:=m(r'b36mix([0-9a-z]+)_(\d{7})'):y,n=int(a[1],36)+1990,a[2][::-1]
 elif a:=m(r'z([0-9a-z]+)\.(\d{4})'):y=int(a[2][::-1]);n=int(a[1],36)-y
 elif a:=m(r'ob([\dOIZSGB]{4})-([\dOIZSGB]+)'):y,n=a[1].translate(TRANS),a[2].translate(TRANS)
 elif a:=m(r'ocrCVE([\dOIZSGB]{4})([\dOIZSGB]{7})'):y,n=a[1].translate(TRANS),a[2].translate(TRANS)
 elif a:=m(r'ocrx([\dOIZSGB]{4})_([\dOIZSGB]+)'):y,n=int(a[1].translate(TRANS))-101,int(a[2].translate(TRANS))-202
 if y is None:return
 y,n=int(y),int(n)
 if not (1999<=y<=2026 and 1<=n<=9999999):return
 return f'CVE-{y}-{n:04d}'
REGS=[re.compile(p) for p in NOISE]+[re.compile(r'[a-z0-9]{3}[!@#$%&?~][A-P]{2}')]
def candidates(raw):
 variants={body(raw)}
 for p in REGS:
  for m in p.finditer(raw):variants.add(body(raw[:m.start()]+raw[m.end():]))
 b=body(raw)
 for p in REGS:
  for m in p.finditer(b):variants.add(b[:m.start()]+b[m.end():])
 return {v for x in variants if (v:=parse(x))}
def options(raw):
 out=set()
 for p in REGS:
  for m in p.finditer(raw):
   v=parse(body(raw[:m.start()]+raw[m.end():]))
   if v:out.add((v,m.group()))
 return out


def main():
    root = Path('/workspace/data')
    output = Path('/workspace/work')
    cves = pd.read_parquet(root / 'vulns_db/cves.parquet')
    kev = pd.read_parquet(root / 'kev_db/kev_entries.parquet')
    kev['canonical'] = kev['notes'].str.extract(
        r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)', expand=False)
    assert kev['canonical'].notna().all()
    kev_ids = set(kev['canonical'])

    cves['options'] = cves['cve_id'].map(options)
    assert cves['options'].map(bool).all()
    token_support = Counter()
    for opts in cves['options']:
        if len({identifier for identifier, token in opts}) == 1:
            token_support.update(token for identifier, token in opts)
    for row in kev.itertuples():
        opts = options(row.cve_ref)
        assert row.canonical in {identifier for identifier, token in opts}
        token_support.update(token for identifier, token in opts
                             if identifier == row.canonical)

    def resolve(opts):
        supported = {identifier for identifier, token in opts
                     if token_support[token] > 0}
        if len(supported) == 1:
            return next(iter(supported))
        # Remaining ambiguous keys cannot affect the requested KEV intersection.
        assert not ({identifier for identifier, token in opts} & kev_ids)
        return None

    cves['canonical'] = cves['options'].map(resolve)
    selected = cves[cves['canonical'].isin(kev_ids)]
    grouped = selected.groupby('canonical').agg(
        row_count=('cve_id', 'size'),
        distinct_vectors=('cvss3_attack_vector', 'nunique'),
        distinct_vectors_with_null=('cvss3_attack_vector',
                                    lambda x: x.nunique(dropna=False)))
    matches = grouped[(grouped['row_count'] > 1) &
                      (grouped['distinct_vectors'] > 1)]
    null_matches = grouped[(grouped['row_count'] > 1) &
                           (grouped['distinct_vectors_with_null'] > 1)]
    assert set(matches.index) == set(null_matches.index)
    selected[selected['canonical'].isin(matches.index)].drop(columns='options').to_csv(
        output / 'matching_rows.csv', index=False)
    matches.to_csv(output / 'matching_cves.csv')
    answer = {'answer': str(len(matches))}
    (output / 'answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(answer))


if __name__ == '__main__':
    main()
