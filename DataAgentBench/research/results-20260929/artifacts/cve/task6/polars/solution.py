import polars as pl
import re,json
from pathlib import Path
D=Path('/workspace/data'); W=Path('/workspace/work')
# Remove the source envelope, then the three-letter wrapper token.
def core(s):
 s=re.sub(r'^[a-z]+-[a-z]{5}(?:::ref=|::key=|::id=|=>|~~|--|__|\+\+|::|[/%#@$~|])','',s)
 s=re.sub(r'^(?:(?:slot|join|ctx|doc|raw|key|id):|[({\[<])?','',s)
 s=re.sub(r'^[a-z]{3}(?:::|[~#@|/:])?','',s)
 m=re.search(r':(?:id|key|slot|join|ctx|doc|raw)[a-z]{3}|=>|[})\]>]|(?:::|~~|--|__|\+\+|[/%#@$~|])(?:aux=|via=|end=)?[a-z]+-[a-z]{4}',s)
 if m:
  head=s[:m.start()]
  if not (m[0].startswith((':id',':key',':slot',':join',':ctx',':doc',':raw')) or m[0][0] in '})]>'):
   head=re.sub(r'[a-p]{3}$','',head)
  s=head
 return s
patterns=[r'[A-P]{2}\d{2}[?%][A-P]',r'[A-P]{2}[@~][A-P]{3}',r'[A-P]{2}[!#$&]\d{3}',r'[A-P]{3}[!$]\d{2}',r'\d{2}[?%][A-P]{2}[a-z0-9]',r'[A-P]{2}[a-z0-9]{3}',r'[a-z0-9]{3}[#&~@][A-P]{2}',r'[a-z0-9]{3}[#&][A-P]{3}',r'\d{3}[?%][A-P]{3}',r'[@~][A-P]{2}[a-z0-9]{3}',r'[A-P][!$][a-z0-9]{3}[A-P]']
def candidates(s):
 s=core(s); out={s}
 for p in patterns:
  for m in re.finditer('(?=('+p+'))',s):out.add(s[:m.start()]+s[m.start()+len(m[1]):])
 return out
def decode(t):
 m=re.fullmatch(r'(?:CVE[-_:]|cve[-_:])?(\d{4})[-_:]{1,2}(\d{4,7})',t)
 if m:return int(m[1]),int(m[2])
 m=re.fullmatch(r'k(\d{4})(\d{7})',t)
 if m:return int(m[1]),int(m[2])
 m=re.fullmatch(r'ord(\d{2})\.(\d{7})',t)
 if m:return 2000+int(m[1]),int(m[2])
 m=re.fullmatch(r'yr(\d+)_n(\d+)',t)
 if m:return 1999+int(m[1]),int(m[2])-17
 m=re.fullmatch(r'n(\d+)_y(\d+)',t)
 if m:return 1900+int(m[2]),int(m[1])-100000
 m=re.fullmatch(r'off(\d+)\.(\d+)',t)
 if m:return int(m[1])-37,int(m[2])-7919
 m=re.fullmatch(r'tri(\d+)-(\d+)',t)
 if m and (int(m[1])-2)%3==0 and (int(m[2])-4)%5==0:return (int(m[1])-2)//3,(int(m[2])-4)//5
 m=re.fullmatch(r'win([+-]\d+)/(\d+)',t)
 if m and (int(m[2])-1)%3==0:return 2010+int(m[1]),(int(m[2])-1)//3
 m=re.fullmatch(r'rv(\d{4})-(\d+)',t)
 if m:return int(m[1][::-1]),int(m[2][::-1])
 m=re.fullmatch(r'z([a-z0-9]+)\.(\d{4})',t)
 if m:return int(m[2][::-1]),int(m[1],36)-int(m[2][::-1])
 m=re.fullmatch(r'h([a-f0-9]+)x([a-f0-9]+)',t)
 if m:return int(m[1],16),int(m[2],16)
 m=re.fullmatch(r'hexmix([a-f0-9]+)_([a-f0-9]+)',t)
 if m:return 1970+int(m[2],10),int(m[1],16)
 m=re.fullmatch(r'b36y([a-z0-9]{3})n([a-z0-9]+)',t)
 if m:return int(m[1],36),int(m[2],36)
 m=re.fullmatch(r'b36mix([a-z0-9]+)_(\d{7})',t)
 if m:return 1990+int(m[1],36),int(m[2][::-1])
 m=re.fullmatch(r'p(\d{2})\d{2}\.(\d{2})\.(\d+)',t)
 if m:return int(m[2]+m[1]),int(m[3])
 m=re.fullmatch(r'mx(\d{2})-(\d{2})-(\d{2})-(\d+)',t)
 if m:return int(m[1]+m[3]),int(m[2]+m[4])
 m=re.fullmatch(r'sp(\d{2})_(\d{2})_(\d+)_(\d{2})',t)
 if m:return int(m[4]+m[2]),int(m[1]+m[3])
 m=re.fullmatch(r'swap(\d{3})-(\d{4})-(\d{4})',t)
 if m:return int(m[2]),int(m[1]+m[3])
 m=re.fullmatch(r'fold(\d{2})(\d{2})-(\d{2})(\d{5})',t)
 if m:return int(m[1]+m[3]),int(m[4]+m[2])
 m=re.fullmatch(r'(i|ri)(\d{11})',t)
 if m:
  z=m[2]; y=z[:8:2]; n=z[1:8:2]+z[8:]
  if m[1]=='ri':y=y[::-1];n=n[::-1]
  return int(y),int(n)
 m=re.fullmatch(r'dot([\d.]+)',t)
 if m:
  z=m[1].replace('.','')
  if len(z)==11:return int(z[:4]),int(z[4:])
 tr=str.maketrans('OIZSGB','012568')
 m=re.fullmatch(r'ob([0-9OIZSGB]{4})-([0-9OIZSGB]+)',t)
 if m:return int(m[1].translate(tr)),int(m[2].translate(tr))
 m=re.fullmatch(r'ocrCVE([0-9OIZSGB]{4})([0-9OIZSGB]{7})',t)
 if m:return int(m[1].translate(tr)),int(m[2].translate(tr))
 m=re.fullmatch(r'ocrx([0-9OIZSGB]{4})_([0-9OIZSGB]+)',t)
 if m:return int(m[1].translate(tr))-101,int(m[2].translate(tr))-202

def recover(s):
 found=set()
 for t in candidates(s):
  try:r=decode(t)
  except ValueError:continue
  if r and 1990<=r[0]<=2030 and 0<r[1]<10000000:found.add(f'CVE-{r[0]}-{r[1]:04d}')
 return sorted(found)

if __name__ == '__main__':
    docs = pl.read_parquet(D / 'descriptions_db/cve_documents.parquet')
    kev = pl.read_parquet(D / 'kev_db/kev_entries.parquet')
    docs = docs.with_columns(pl.col('cve').map_elements(recover, return_dtype=pl.List(pl.String)).alias('ids'))
    kev = kev.with_columns(pl.col('cve_ref').map_elements(recover, return_dtype=pl.List(pl.String)).alias('ids'))
    assert docs.filter(pl.col('ids').list.len() == 0).is_empty(), 'Unparsed description keys'
    assert kev.filter(pl.col('ids').list.len() == 0).is_empty(), 'Unparsed KEV keys'
    # Plain CVE links in KEV notes independently disambiguate encoded catalog keys.
    def kev_id(row):
        ids = set(row['ids'])
        note_ids = set(re.findall(r'CVE-\d{4}-\d+', row['notes'] or ''))
        if note_ids:
            ids &= note_ids
        assert len(ids) == 1, (row['cve_ref'], ids)
        return next(iter(ids))
    kev = kev.with_columns(pl.struct('ids', 'notes', 'cve_ref').map_elements(kev_id, return_dtype=pl.String).alias('cve_id'))
    catalog_ids = kev['cve_id'].unique().to_list()
    # All possible decodings of excluded rows are outside KEV. Each relevant row
    # must have exactly one decoding overall, so language aggregation is exact.
    docs = docs.filter(pl.col('ids').list.set_intersection(pl.lit(catalog_ids)).list.len() > 0)
    assert docs.filter(pl.col('ids').list.len() != 1).is_empty(), 'Ambiguous KEV-linked description key'
    docs = docs.with_columns(pl.col('ids').list.first().alias('cve_id'))
    dtype = pl.List(pl.Struct({'lang': pl.String, 'value': pl.String}))
    descriptions = (docs.select('cve_id', pl.col('descriptions').str.json_decode(dtype))
                    .explode('descriptions').unnest('descriptions'))
    language_flags = descriptions.group_by('cve_id').agg(
        (pl.col('lang') == 'en').any().alias('has_english'),
        (pl.col('lang').is_not_null() & (pl.col('lang') != 'en')).any().alias('has_non_english'))
    result = (language_flags.filter(~pl.col('has_english') & pl.col('has_non_english'))
              .join(kev.select('cve_id').unique(), on='cve_id', how='semi')
              .select('cve_id').unique().sort('cve_id'))
    result.write_csv(W / 'qualifying_cves.csv')
    answer = {'answer': str(result.height)}
    (W / 'answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(answer))
