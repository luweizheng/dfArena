import json
import re
from pathlib import Path
import ibis

# Scalar decoding is applied inside the lazy Ibis query as DuckDB Python UDFs.
NOISE = re.compile(r'(?:[a-z0-9]{3}[!@#$%&?~][A-P]{3}|[0-9][!@#$%&?~][A-P]{2}[0-9]{2}|[A-P]{2}[!@#$%&?~][A-P]{3}|[A-P]{2}[0-9]{2}[!@#$%&?~][A-P]|[A-P]{3}[!@#$%&?~][0-9]{2}|[!@#$%&?~][A-P]{3}[0-9]{2}|[a-z0-9]{2}[!@#$%&?~][A-P]{3}|[0-9]{2}[!@#$%&?~][A-P]{2}[a-z0-9]|[!@#$%&?~][A-P]{2}[a-z0-9]{3}|[A-P]{2}[!@#$%&?~][a-z0-9]{3}|[A-P][!@#$%&?~][a-z0-9]{3}[A-P]|[a-z0-9]{3}[!@#$%&?~][A-P]{2})')
OCR = str.maketrans('OZISBG','021586')
def decoded_candidates(value):
    variants = []
    for width in (6,7):
        for i in range(len(value)-width+1):
            if NOISE.fullmatch(value[i:i+width]):
                frag=value[i:i+width]
                rank=(width, sum(c.isupper() for c in frag), bool(re.fullmatch(r'[a-z0-9]{3}[!@#$%&?~][A-P]{2}',frag)), re.search(r'[!@#$%&?~]',frag).start())
                variants.append((rank,value[:i]+value[i+width:]))
    if not variants: variants = [((0,0,False),value)]
    ranked = []
    out = set()
    def add(y,n):
        y,n=int(y),int(n)
        if 1999 <= y <= 2030 and 0 < n < 10000000:
            out.add(f'CVE-{y}-{n:04d}')
    for rank,s in variants:
        out=set()
        for p,fn in [
            (r'ob([0-9OZISBG]{4})-([0-9OZISBG]{4,7})',lambda m:(m[1].translate(OCR),m[2].translate(OCR))),
            (r'ocrCVE([0-9OZISBG]{4})([0-9OZISBG]{7})',lambda m:(m[1].translate(OCR),m[2].translate(OCR))),
            (r'ocrx([0-9OZISBG]{4})_([0-9OZISBG]{4,7})',lambda m:(int(m[1].translate(OCR))-101,int(m[2].translate(OCR))-202)),
            (r'yr(\d{2})_n(\d+)',lambda m:(2000+int(m[1])-1,int(m[2])-17)),
            (r'n(\d+)_y(\d+)',lambda m:(1900+int(m[2]),int(m[1])-100000)),
            (r'b36y([0-9a-z]+)n([0-9a-z]+)(?=[:>}\]])',lambda m:(int(m[1],36),int(m[2],36))),
            (r'b36mix([0-9a-z]+)_(\d{7})',lambda m:(1990+int(m[1],36),int(m[2][::-1]))),
            (r'hexmix([0-9a-f]+)_(\d+)',lambda m:(1970+int(m[2]),int(m[1],16))),
            (r'h([0-9a-f]+)x([0-9a-f]+)',lambda m:(int(m[1],16),int(m[2],16))),
            (r'z([0-9a-z]+)\.(\d{4})',lambda m:(int(m[2][::-1]),int(m[1],36))),
            (r'rv(\d{4})-(\d+)',lambda m:(int(m[1][::-1]),int(m[2][::-1]))),
            (r'swap(\d{3})-(\d{4})-(\d{4})',lambda m:(m[2],m[1]+m[3])),
            (r'mx(\d{2})-(\d{2})-(\d{2})-(\d{3})',lambda m:(m[1]+m[3],m[2]+m[4])),
            (r'p(\d{2})\d{2}\.(\d{2})\.(\d+)',lambda m:(m[2]+m[1],m[3])),
            (r'fold(\d{2})(\d{2})-(\d{2})(\d{5})',lambda m:(m[1]+m[3],m[4]+m[2])),
            (r'ord(\d{2})\.(\d{7})',lambda m:(2000+int(m[1]),m[2])),
            (r'win\+(\d+)/(\d+)',lambda m:(2010+int(m[1]),(int(m[2])-1)//3)),
            (r'tri(\d+)-(\d+)',lambda m:((int(m[1])-2)//3,(int(m[2])-4)//5)),
            (r'k(\d{4})q?(\d{7})',lambda m:(m[1],m[2])),
            (r'(?:CVE[-_:]|cve[-:])?(20\d{2})[-_:]+(\d{4,7})(?=[:>}\])])',lambda m:(m[1],m[2])),
        ]:
            before=len(out)
            for m in re.finditer(p,s):
                try: add(*fn(m))
                except ValueError: pass
            if len(out)>before: break
        for m in re.finditer(r'dot([0-9.]+)',s):
            d=m[1].replace('.','')
            if len(d)==11: add(d[:4],d[4:])
        for m in re.finditer(r'(ri|i)(\d{11})(?!\d)',s):
            d=m[2];y=d[:8:2];n=d[1:8:2]+d[8:]
            if m[1]=='ri': y,n=y[::-1],n[::-1]
            add(y,n)
        if out: ranked.append((rank,out))
    if not ranked: return []
    best=max(rank for rank,out in ranked)
    return sorted(set().union(*(out for rank,out in ranked if rank==best)))

@ibis.udf.scalar.python
def decode_cve(s: str) -> list[str]:
    return decoded_candidates(s)

@ibis.udf.scalar.python
def normalize_version(s: str) -> str:
    if s.startswith('build-'):
        p=s[6:]
        if p.isdigit() and len(p)%3==0:
            return '.'.join(str(int(p[i:i+3])) for i in range(0,len(p),3))
        raise ValueError('Unrecognized build version: '+s)
    return re.sub(r'[, _]', '.', re.sub(r'^v(?=\d)', '', s.strip().lower()))

def main():
    con=ibis.duckdb.connect()
    def read(p): return con.read_parquet('/workspace/data/'+p+'.parquet')
    m=read('cpe_db/cpe_matches')
    a=read('cpe_db/vendor_aliases')
    v=read('cpe_db/cpe_version_details')
    k=read('kev_db/kev_entries')
    # All KEV rows have an unambiguous NVD identity in their notes. This gives
    # the canonical key directly, without using KEV's product labels.
    k=k.mutate(canonical_cve=k.notes.re_extract(r'(?i)nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)',1).upper())
    missing=k.filter(k.canonical_cve.isnull() | (k.canonical_cve==''))
    assert missing.count().execute()==0, 'KEV rows lacking NVD identity'
    m=m.mutate(alias=ibis.ifelse(m.criteria.startswith('cpe:'),m.criteria.split(':')[3],m.criteria.re_extract(r'^([^/ ]+)',1)),product=ibis.ifelse(m.criteria.startswith('cpe:'),m.criteria.split(':')[4],m.criteria.re_extract(r'^[^/ ]+[/ ]([^@ ]+)',1)).lower())
    m=m.join(a,m['alias']==a['alias']).filter(a.canonical_vendor=='apache',m.product=='tomcat')
    m=m.filter(m.vulnerable_flag.strip().lower().isin(['1','true','t','yes','y','v','vulnerable','affected']))
    t=v.semi_join(m,['cve_id','criteria']).filter(v.version_text.notnull(),v.version_text!='*')
    t=t.mutate(candidates=decode_cve(t.cve_id),version=normalize_version(t.version_text))
    audit=t.select('cve_id','criteria','version','candidates').distinct().to_pyarrow().to_pylist()
    Path('/workspace/work/decoding_audit.json').write_text(json.dumps(audit,indent=2))
    missing=t.filter(t.candidates.length()==0)
    assert missing.count().execute()==0, 'Undecoded CPE identifiers; inspect decoding_audit.json'
    assert t.filter(t.candidates.length()!=1).count().execute()==0, 'Ambiguous CVE decoding'
    assert t.count().execute()>0, 'No eligible Tomcat version rows'
    t=t.mutate(canonical_cve=t.candidates.unnest())
    result=t.semi_join(k,'canonical_cve').select('version').distinct().order_by('version')
    versions=result.to_pyarrow().column('version').to_pylist()
    count=int(result.count().execute())
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(count)}))
    print(json.dumps({'count':count,'versions':versions}))

if __name__=='__main__': main()
