import re
PATTERNS=[r'[A-P]{2}\d{2}[?%][A-P]',r'\d{2}[?%][A-P]{2}[a-z0-9]',r'[A-P]{2}[~@][A-P]{3}',r'[A-P]{3}[!$]\d{2}',r'[A-P][!$][a-z0-9]{3}[A-P]',r'[a-z0-9]{3}[#&@~][A-P]{3}',r'[a-z0-9]{3}[#&@~][A-P]{2}',r'\d{3}[?%][A-P]{3}',r'[A-P]{2}[#!&$]\d{3}',r'[~@][A-P]{2}[a-z0-9]{3}']
def unwrap(s):
 s=re.sub(r'^[a-z]+-[a-p]{5}(?:::ref=|::key=|::id=|::|=>|\+\+|--|__|~~|[~/#%@$|])','',s)
 s=re.sub(r'^(?:(?:doc|id|key|slot|ctx|raw|join):|[\[({<])?[a-p]{3}(?:::|[~/#:@|])?','',s)
 s=re.split(r':(?:ctx|raw|id|key|slot|doc|join)[a-p]{3}',s)[0]
 s=re.sub(r'[a-p]{3}(?:::|=>|\+\+|--|__|~~|[~/#%@$|]).*$','',s)
 s=re.split(r'[\])}>]',s)[0]
 return s

def core(s):
 m=re.fullmatch(r'(?:CVE[-_]|cve[-:])?(\d{4})[-_:]{1,2}(\d+)',s)
 if m:return tuple(map(int,m.groups()))
 if s.startswith(('ob','ocrCVE','ocrx')):
  mode='ob' if s.startswith('ob') else ('ocrx' if s.startswith('ocrx') else 'ocrCVE')
  t=s[len(mode):].translate(str.maketrans('OIZSBG','012586'))
  if mode=='ob':return core(t)
  if mode=='ocrCVE' and t.isdigit():return int(t[:4]),int(t[4:])
  if mode=='ocrx':
   y,n=map(int,t.split('_'));return y-101,n-202
 if s.startswith('k') and s[1:].isdigit():return int(s[1:5]),int(s[5:])
 if s.startswith('dot'):return core('k'+s[3:].replace('.',''))
 if s.startswith('i') and s[1:].isdigit():
  t=s[1:];return int(t[:8:2]),int(t[1:8:2]+t[8:]) # inspect
 if s.startswith('ri') and s[2:].isdigit():
  t=s[2:];return int(t[:8:2][::-1]),int((t[1:8:2]+t[8:])[::-1])
 m=re.fullmatch(r'off(\d+)\.(\d+)',s)
 if m:return int(m[1])-37,int(m[2])-7919
 m=re.fullmatch(r'yr(\d+)_n(\d+)',s)
 if m:return int(m[1])+1999,int(m[2])-17
 m=re.fullmatch(r'n(\d+)_y(\d+)',s)
 if m:return int(m[2])+1900,int(m[1])-100000
 m=re.fullmatch(r'rv(\d+)-(\d+)',s)
 if m:return int(m[1][::-1]),int(m[2][::-1])
 m=re.fullmatch(r'h([0-9a-f]+)x([0-9a-f]+)',s)
 if m:return int(m[1],16),int(m[2],16)
 m=re.fullmatch(r'b36y([a-z0-9]{3})n([a-z0-9]+)',s)
 if m:return int(m[1],36),int(m[2],36)
 m=re.fullmatch(r'z([a-z0-9]+)\.(\d+)',s)
 if m:return int(m[2][::-1]),int(m[1],36)-int(m[2][::-1])
 m=re.fullmatch(r'ord(\d+)\.(\d+)',s)
 if m:return int(m[1])+2000,int(m[2])
 m=re.fullmatch(r'win\+(\d+)/(\d+)',s)
 if m:return int(m[1])+2010,(int(m[2])-1)//3
 m=re.fullmatch(r'tri(\d+)-(\d+)',s)
 if m:return (int(m[1])-2)//3,(int(m[2])-4)//5
 m=re.fullmatch(r'p(\d{2})(\d{2})\.(\d+)\.(\d+)',s)
 if m:return int(m[3]+m[1]),int(m[4]) # second chunk validation later
 m=re.fullmatch(r'mx(\d+)-(\d+)-(\d+)-(\d+)',s)
 if m:return int(m[1]+m[3]),int(m[2]+m[4])
 m=re.fullmatch(r'sp(\d+)_(\d+)_(\d+)_(\d+)',s)
 if m:return int(m[4]+m[2]),int(m[1]+m[3])
 m=re.fullmatch(r'swap(\d+)-(\d+)-(\d+)',s)
 if m:return int(m[2]),int(m[1]+m[3])
 m=re.fullmatch(r'fold(\d{2})(\d{2})-(\d{2})(\d+)',s)
 if m:return int(m[1]+m[3]),int(m[4]+m[2])
 m=re.fullmatch(r'hexmix([0-9a-f]+)_([0-9a-f]+)',s)
 if m:return int(m[2])+1970,int(m[1],16)
 m=re.fullmatch(r'b36mix([a-z0-9]+)_(\d+)',s)
 if m:return int(m[1],36)+1990,int(m[2][::-1])
 raise ValueError(s)

def candidates(s):
 out=set()
 for p in PATTERNS:
  for m in re.finditer('(?=('+p+'))',s):
   t=s[:m.start()]+s[m.start()+len(m[1]):]
   try:
    y,n=core(unwrap(t))
    if 1990<=y<=2030 and n>0:out.add(f'CVE-{y}-{n:04d}')
   except (ValueError,TypeError):pass
 return out


if __name__ == '__main__':
    import json
    from pathlib import Path
    import pandas as pd

    root = Path('/workspace/data')
    registry = pd.read_parquet(root / 'vulns_db/cves.parquet')
    kev = pd.read_parquet(root / 'kev_db/kev_entries.parquet')
    matches = pd.read_parquet(root / 'cpe_db/cpe_matches.parquet')
    aliases = pd.read_parquet(root / 'cpe_db/vendor_aliases.parquet')

    # The three observed criteria formats are CPE 2.3, vendor/product@version,
    # and vendor Product Version. Resolve the vendor through the supplied table.
    matches['alias'] = matches.criteria.str.extract(
        r'^(?:cpe:2\.3:[^:]+:)?([^:/\s]+)', expand=False)
    matches = matches.merge(aliases, on='alias', how='left', validate='many_to_one')
    truthy = {'t', 'y', 'yes', 'affected', 'vulnerable', 'v', 'true', '1'}
    flags = matches.vulnerable_flag.str.strip().str.lower()
    apache = matches.loc[matches.canonical_vendor.eq('apache') & flags.isin(truthy)].copy()

    # Retain all plausible decodings where injected noise has multiple parses.
    # A lower/upper-bound check below proves those ambiguities cannot affect
    # the answer: every included CVE has an unambiguous witness in each table.
    for frame, key in [(registry, 'cve_id'), (kev, 'cve_ref'), (apache, 'cve_id')]:
        frame['ids'] = frame[key].map(candidates)
        assert frame.ids.map(len).gt(0).all(), 'Unparsed CVE identifier'

    # Independently check the decoder against original CVE links in KEV notes.
    for row in kev.itertuples():
        links = re.findall(r'nvd.nist.gov/vuln/detail/(CVE-\d+-\d+)', row.notes or '')
        if links:
            assert links[0] in row.ids, (row.cve_ref, links[0], row.ids)

    published = pd.to_datetime(registry.published, errors='raise')
    registry = registry.loc[published.dt.year.eq(2023)]

    def intersect_frames(unambiguous_only):
        tables = []
        for frame in [registry, kev, apache]:
            if unambiguous_only:
                frame = frame.loc[frame.ids.map(len).eq(1)]
            tables.append(frame[['ids']].explode('ids').drop_duplicates())
        return tables[0].merge(tables[1], on='ids').merge(tables[2], on='ids')

    upper = intersect_frames(False)
    lower = intersect_frames(True)
    assert set(upper.ids) == set(lower.ids), 'Ambiguity affects the result'
    result = upper.sort_values('ids').reset_index(drop=True)
    result.to_csv('/workspace/work/matching_cves.csv', index=False)
    answer = {'answer': str(result.ids.nunique())}
    Path('/workspace/work/answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(answer))
