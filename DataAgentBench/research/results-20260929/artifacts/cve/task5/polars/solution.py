import re,json
from pathlib import Path
import polars as pl
D=Path('/workspace/data'); W=Path('/workspace/work')
OCR=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
def decode(s):
    variants=[s]+[s[:i]+s[i+length:] for length in (6,7) for i in range(len(s)-length+1) if re.search(r'[!@#$%&?~]',s[i:i+length]) and re.search('[A-P]',s[i:i+length])]
    out=set()
    def add(y,n):
        y,n=int(y),int(n)
        if 1990<=y<=2030 and 1<=n<=9999999:out.add(f'CVE-{y}-{n:04d}')
    for t in variants:
        for a,b in re.findall(r'(20\d{2})[-_:]+(\d{4,7})(?!\d)',t):add(a,b)
        for a,b in re.findall(r'rv(\d{4})-(\d+)',t):add(a[::-1],b[::-1])
        for a,b in re.findall(r'n1(\d+)_y1(\d{2})',t):add(2000+int(b),a)
        for a,b in re.findall(r'yr(\d{2})_n(\d+)',t):add(1999+int(a),int(b)-17)
        for a,b in re.findall(r'hexmix([0-9a-f]+)_(\d+)',t):add(1970+int(b),int(a,16))
        for a,b in re.findall(r'h([0-9a-f]{3})x([0-9a-f]+)',t):add(int(a,16),int(b,16))
        for a,b in re.findall(r'b36y([0-9a-z]+)n([0-9a-z]+)',t):
            try:add(int(a,36),int(b,36))
            except ValueError:pass
        for a,b in re.findall(r'b36mix([0-9a-z]+)_(\d+)',t):add(1990+int(a,36),b[::-1])
        for a,b in re.findall(r'z([0-9a-z]+)\.(\d{4})',t):add(b[::-1],int(a,36)-11)
        for a,b in re.findall(r'win\+(\d+)/(\d+)',t):
            if (int(b)-1)%3==0:add(2010+int(a),(int(b)-1)//3)
        for a,b in re.findall(r'ord(\d{2})\.(\d+)',t):add(2000+int(a),b)
        for a,b,c in re.findall(r'fold(\d{4})-(\d{2})(\d+)',t):add(2000+int(b),c+a[2:])
        for a,b,c in re.findall(r'swap(\d{3})-(\d{4})-(\d+)',t):add(b,a+c)
        for a,b,c,d in re.findall(r'mx(\d{2})-(\d{2})-(\d{2})-(\d+)',t):add(a+c,b+d)
        for a,b,c in re.findall(r'p(\d{2})\d{2}\.(\d{2})\.(\d+)',t):add(b+a,c)
        for a,b in re.findall(r'tri(\d+)-(\d+)',t):
            if (int(a)-11)%3==0 and (int(b)-4)%5==0:add((int(a)-11)//3,(int(b)-4)//5)
        for a,b in re.findall(r'off(\d{4})\.(\d+)',t):add(int(a)-37,int(b)-9000)
        for a in re.findall(r'dot([\d.]+)',t):
            z=a.replace('.','');
            if len(z)>=8:add(z[:4],z[4:])
        for a in re.findall(r'k(20\d{9})',t):add(a[:4],a[4:])
        for a in re.findall(r'ri(\d{11})',t):
            add(a[:8:2][::-1],(a[1:8:2]+a[8:])[::-1])
        for a in re.findall(r'i(\d{11})',t):add(a[:8:2],a[1:8:2]+a[8:])
        u=t.translate(OCR)
        for a,b in re.findall(r'ob(\d{4})-(\d+)',u):add(a,b)
        for a,b in re.findall(r'ocrx(\d{4})_(\d+)',u):add(int(a)-101,int(b)-202)
        for a in re.findall(r'ocrCVE(\d{11})',u):add(a[:4],a[4:])
    return sorted(out)

def product(s):
    if s.startswith('cpe:'):return s.split(':')[3:5]
    if '/' in s:return [s.split('/')[0],s.split('/')[1].split('@')[0]]
    parts=s.split();return [parts[0],'_'.join(parts[1:-1]).lower()]

m=pl.read_parquet(D/'cpe_db/cpe_matches.parquet').with_columns(pl.col('criteria').map_elements(lambda s:dict(zip(['alias','product'],product(s))),return_dtype=pl.Struct({'alias':pl.String,'product':pl.String})).alias('parsed')).unnest('parsed')
m=m.join(pl.read_parquet(D/'cpe_db/vendor_aliases.parquet'),on='alias').filter((pl.col('canonical_vendor')=='apache')&(pl.col('product')=='tomcat'))
keys=m.select('cve_id').unique().with_columns(pl.col('cve_id').map_elements(decode,return_dtype=pl.List(pl.String)).alias('ids'))
assert keys.filter(pl.col('ids').list.len()==0).is_empty()
keys.write_json(W/'decoded_keys.json')
k=pl.read_parquet(D/'kev_db/kev_entries.parquet').with_columns(pl.col('notes').str.extract(r'https?://nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)').alias('id'))
assert k['id'].null_count()==0
# Resolve ambiguous noise boundaries by support from independently encoded rows.
# The correct identifier is repeated across different encoding families.
candidates=keys.explode('ids')
support=candidates.group_by('ids').agg(pl.col('cve_id').n_unique().alias('support'))
ranked=candidates.join(support,on='ids').with_columns(pl.col('support').max().over('cve_id').alias('best')).filter(pl.col('support')==pl.col('best'))
assert ranked['cve_id'].n_unique()==keys.height
ambiguous=ranked.group_by('cve_id').len().filter(pl.col('len')>1)
resolved=ranked.select('cve_id','ids')
assert ambiguous.join(ranked,on='cve_id').join(k.select(pl.col('id').alias('ids')),on='ids').is_empty(), 'Ambiguous KEV membership'
selected=m.join(resolved,on='cve_id').join(k.select(pl.col('id').alias('ids')).unique(),on='ids').filter(pl.col('vulnerable_flag').str.to_lowercase().is_in(['true','t','yes','y','1','affected','vulnerable','v']))
v=pl.read_parquet(D/'cpe_db/cpe_version_details.parquet')
selected=selected.join(v,on=['cve_id','criteria'])
def version(s):
    if s is None or s=='*':return None
    if s.startswith('build-'):
        b=s[6:];assert b.isdigit() and len(b)%3==0
        return '.'.join(str(int(b[i:i+3])) for i in range(0,len(b),3))
    return re.sub(r'[, _]','.',re.sub(r'^v','',s))
selected=selected.with_columns(pl.col('version_text').map_elements(version,return_dtype=pl.String).alias('version'))
versions=selected.select('version').drop_nulls().unique().sort('version')
selected.write_csv(W/'matched_versions.csv')
versions.write_csv(W/'distinct_versions.csv')
answer=f"{versions.height} distinct affected versions."
(W/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(answer,versions.to_dicts())
