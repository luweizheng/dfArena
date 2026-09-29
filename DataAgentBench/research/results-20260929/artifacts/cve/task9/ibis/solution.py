import re,json
from pathlib import Path
import ibis

# Each surface key wraps an encoded identifier and one inserted noise fragment.
NOISE=[r'[0-9]{3}[?%][A-P]{3}',r'[A-P]{2}[@~][A-P]{3}',r'[A-P]{3}[!$][0-9]{2}',r'[A-P]{2}[0-9]{2}[?%][A-P]',r'[A-P][!$][a-z0-9]{3}[A-P]',r'[@~][A-P]{2}[a-z0-9]{3}',r'[0-9]{2}[?%][A-P]{2}[a-z0-9]',r'[A-P]{2}[#$!&][0-9]{3}',r'[a-z0-9]{3}[#&@~][A-P]{2,3}']

def core(s):
 s=re.sub(r'^[a-z]+-[a-p]{5}(?:::ref=|::key=|::id=|::|=>|--|__|~~|\+\+|[@/#~%$|])','',s)
 s=re.sub(r'^(?:(?:doc|raw|slot|key|ctx|id|join):|[({<\[])?[a-p]{3}(?:::|[:/@#~|])?','',s)
 s=re.sub(r'(?::(?:doc|raw|slot|key|ctx|id|join)[a-p]{3}|[)}\]>][a-p]{3}|[a-p]{3})(?:::|=>|--|__|~~|\+\+|[@/#~%$|]).*$','',s)
 return s

def variants(s):
 out=set()
 for p in NOISE:
  for m in re.finditer(p,s):
   out.add(core(s[:m.start()]+s[m.end():]))
   # Both two- and three-letter noise suffixes occur.
   if p==NOISE[-1] and re.search(r'[A-P]{3}$',m[0]):
    out.add(core(s[:m.start()]+s[m.end()-1:]))
 return out or {core(s)}

OCR=str.maketrans({'O':'0','I':'1','Z':'2','S':'5','G':'6','B':'8'})
def parse(s):
 def m(p): return re.fullmatch(p,s)
 z=None
 if q:=m(r'(?:CVE[-_]|cve[-:])?(\d{4})[-_:](\d+)'): z=(int(q[1]),int(q[2]))
 elif q:=m(r'(\d{4})::(\d+)'): z=(int(q[1]),int(q[2]))
 elif q:=m(r'k(\d{4})(\d{7})'): z=(int(q[1]),int(q[2]))
 elif q:=m(r'ord(\d{2})\.(\d{7})'): z=(2000+int(q[1]),int(q[2]))
 elif q:=m(r'off(\d{4})\.(\d+)'): z=(int(q[1])-37,int(q[2])-7919)
 elif q:=m(r'yr(\d+)_n(\d+)'): z=(1999+int(q[1]),int(q[2])-17)
 elif q:=m(r'n(\d+)_y(\d+)'): z=(1900+int(q[2]),int(q[1])-100000)
 elif q:=m(r'win\+(\d+)/(\d+)'):
  if (int(q[2])-1)%3==0: z=(2010+int(q[1]),(int(q[2])-1)//3)
 elif q:=m(r'tri(\d+)-(\d+)'):
  if (int(q[1])-2)%3==0 and (int(q[2])-4)%5==0: z=((int(q[1])-2)//3,(int(q[2])-4)//5)
 elif q:=m(r'rv(\d{4})-(\d+)'): z=(int(q[1][::-1]),int(q[2][::-1]))
 elif q:=m(r'z([a-z0-9]+)\.(\d{4})'): z=(int(q[2][::-1]),int(q[1],36)-int(q[2][::-1]))
 elif q:=m(r'h([a-f0-9]+)x([a-f0-9]+)'): z=(int(q[1],16),int(q[2],16))
 elif q:=m(r'b36y([a-z0-9]{3})n([a-z0-9]+)'): z=(int(q[1],36),int(q[2],36))
 elif q:=m(r'b36mix([a-z0-9]+)_(\d{7})'): z=(1990+int(q[1],36),int(q[2][::-1]))
 elif q:=m(r'hexmix([a-f0-9]+)_([a-f0-9]+)'): z=(1970+int(q[2]),int(q[1],16))
 elif q:=m(r'p(\d{2})\d{2}\.(\d{2})\.(\d+)'): z=(int(q[2]+q[1]),int(q[3]))
 elif q:=m(r'mx(\d{2})-(\d+)-(\d{2})-(\d+)'): z=(int(q[1]+q[3]),int(q[2]+q[4]))
 elif q:=m(r'sp(\d+)_(\d{2})_(\d+)_(\d{2})'): z=(int(q[4]+q[2]),int(q[1]+q[3]))
 elif q:=m(r'swap(\d+)-(\d{4})-(\d+)'): z=(int(q[2]),int(q[1]+q[3]))
 elif q:=m(r'fold(\d{4})-(\d{7})'):
  digits=q[1][:2]+q[2]+q[1][2:];z=(int(digits[:4]),int(digits[4:]))
 elif q:=m(r'(ri|i)(\d{11})'):
  y=q[2][:8:2];n=q[2][1:8:2]+q[2][8:]
  if q[1]=='ri': y=y[::-1];n=n[::-1]
  z=(int(y),int(n))
 elif q:=m(r'dot([0-9.]+)'):
  digits=q[1].replace('.','')
  if len(digits)==11:z=(int(digits[:4]),int(digits[4:]))
 elif q:=m(r'ob([0-9OIZSGB]{4})-([0-9OIZSGB]+)'):z=(int(q[1].translate(OCR)),int(q[2].translate(OCR)))
 elif q:=m(r'ocrCVE([0-9OIZSGB]{11})'):
  digits=q[1].translate(OCR);z=(int(digits[:4]),int(digits[4:]))
 elif q:=m(r'ocrx([0-9OIZSGB]{4})_([0-9OIZSGB]+)'): z=(int(q[1].translate(OCR))-101,int(q[2].translate(OCR))-202)
 if z and 1990<=z[0]<=2030 and 0<=z[1]<10000000:return f'CVE-{z[0]}-{z[1]:04d}'
 return None

def candidates(s):return sorted({v for x in variants(s) if (v:=parse(x))})


@ibis.udf.scalar.python
def decode_options(s:str)->list[str]:
 return candidates(s)
@ibis.udf.scalar.python
def kev_options(s:str,notes:str)->list[str]:
 vals=candidates(s)
 refs=re.findall(r'nvd.nist.gov/vuln/detail/(CVE-\d{4}-\d+)',notes or '')
 confirmed=sorted(set(vals)&set(refs))
 return confirmed if confirmed else vals


def main():
    con = ibis.duckdb.connect()
    c = con.read_parquet('/workspace/data/vulns_db/cves.parquet')
    k = con.read_parquet('/workspace/data/kev_db/kev_entries.parquet')
    c = c.mutate(options=decode_options(c.cve_id))
    k = k.mutate(options=kev_options(k.cve_ref, k.notes.fill_null('')))
    assert c.filter(c.options.length() == 0).count().execute() == 0
    assert k.filter(k.options.length() != 1).count().execute() == 0
    kev_ids = k.select(canonical=k.options.unnest()).distinct()

    # Noise can occasionally admit multiple syntactically valid decodings.
    # Compute rigorous lower/upper bounds rather than guess: the lower bound
    # uses only uniquely decoded registry rows; the upper includes every option.
    bounds = []
    for certain_only in (True, False):
        registry = c.filter(c.options.length() == 1) if certain_only else c
        registry = registry.mutate(canonical=registry.options.unnest())
        grouped = registry.group_by('canonical').aggregate(
            row_count=registry.count(),
            vector_count=registry.cvss3_attack_vector.nunique(),
            vector_count_with_null=registry.cvss3_attack_vector.fill_null('<NULL>').nunique(),
        )
        conflicting = grouped.filter(
            (grouped.row_count > 1) & (grouped.vector_count > 1)
        )
        matched = conflicting.semi_join(kev_ids, 'canonical')
        bounds.append(int(matched.count().execute()))
        # Verify that treating missing vectors as a separate value cannot
        # change the requested intersection in this snapshot.
        null_only = grouped.filter(
            (grouped.vector_count <= 1) & (grouped.vector_count_with_null > 1)
        ).semi_join(kev_ids, 'canonical')
        assert null_only.count().execute() == 0
    assert bounds[0] == bounds[1], f'Unresolved count bounds: {bounds}'
    answer = {'answer': str(bounds[0])}
    Path('/workspace/work/answer.json').write_text(json.dumps(answer) + '\n')
    print(json.dumps(answer))


if __name__ == '__main__':
    main()
