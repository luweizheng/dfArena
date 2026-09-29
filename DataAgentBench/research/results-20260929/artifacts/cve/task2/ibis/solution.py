import ibis, re, json
from pathlib import Path
con=ibis.duckdb.connect()
k=con.read_parquet('/workspace/data/kev_db/kev_entries.parquet')
a=con.read_parquet('/workspace/data/kev_db/kev_vendor_aliases.parquet')
s=con.read_parquet('/workspace/data/vulns_db/cvss_metadata.parquet')
k=k.filter(k.known_ransomware_use.strip().lower()=='known').mutate(cid=k.notes.re_extract(r'nvd\.nist\.gov/vuln/detail/(CVE-[0-9]{4}-[0-9]+)',1))
k=k.join(a,'vendor_project').select('cid','canonical_vendor').distinct()
keys=k.cid.to_pyarrow().to_pylist()
assert all(keys)
# Generate common reversible identifier encodings; preserve leading zero variants.
forms={}
def b36(n):
 out=''
 while n: n,r=divmod(n,36); out='0123456789abcdefghijklmnopqrstuvwxyz'[r]+out
 return out or '0'
def norm(s): return s.translate(str.maketrans('OIZSGB','012568')).replace('.','')
def add(form,key): forms.setdefault(norm(form),set()).add(key)
for key in keys:
 y,n=key[4:].split('-'); Y,N=int(y),int(n)
 for nn in {n,str(N),str(N).zfill(7)}:
  for sep in ['-', '_', ':','::']:
   add(y+sep+nn,key)
  add('mx'+y[:2]+'-'+nn[:2]+'-'+y[2:]+'-'+nn[2:],key)
  add('sp'+nn[:2]+'_'+y[2:]+'_'+nn[2:]+'_'+y[:2],key)
  add('rv'+y[::-1]+'-'+nn[::-1],key)
  add('h'+format(Y,'x')+'x'+format(N,'x'),key)
  add('off'+str(Y+37)+'.'+str(N+7919),key)
  add('n'+str(N+100000)+'_y'+str(Y-1900),key)
 nn=str(N).zfill(7)
 inter=''.join(a+b for a,b in zip(y,nn[:4]))+nn[4:]
 for f in ['k'+y+nn,'i'+inter,'ri'+''.join(a+b for a,b in zip(y[::-1],nn[::-1][:4]))+nn[::-1][4:],
           'p'+y[2:]+str(N%97).zfill(2)+'.'+y[:2]+'.'+str(N),
           'yr'+str(Y-1999)+'_n'+str(N+17),
           'tri'+str(Y*3+2)+'-'+str(N*5+4),
           'win+'+str(Y-2010)+'/'+str(N*3+1),
           'fold'+y[:2]+nn[-2:]+'-'+y[2:]+nn[:-2],
           'swap'+nn[:3]+'-'+y+'-'+nn[3:],
           'sp'+nn[:2]+'_'+y[2:]+'_'+nn[2:]+'_'+y[:2],
           'sp'+n[:2]+'_'+y[2:]+'_'+n[2:]+'_'+y[:2],
           'mx'+y[:2]+'-'+n[:2]+'-'+y[2:]+'-'+n[2:],
           'b36mix'+b36(Y-1990)+'_'+nn[::-1],
           'hexmix'+format(N,'x')+'_'+str(Y-1970),
           'z'+b36(N+Y)+'.'+y[::-1],
           'b36y'+b36(Y)+'n'+b36(N),
           'ob'+y+'-'+n,'ocrCVE'+y+nn,
           'ocrx'+str(Y+101)+'_'+str(N+202),
           'ord'+y[2:]+'.'+nn,'dot'+y+nn]: add(f,key)
# A single short infix containing punctuation obscures otherwise intact forms.
# Enumerate its removal without imposing guessed random-noise alphabets.
def trie_pattern(words):
 tree={}
 for word in words:
  node=tree
  for char in word: node=node.setdefault(char,{})
  node['']=True
 def build(node):
  terms=[re.escape(c)+build(v) for c,v in node.items() if c]
  out='(?:'+'|'.join(terms)+')' if len(terms)>1 else (terms[0] if terms else '')
  return '(?:'+out+')?' if '' in node and terms else out
 return build(tree)
pattern=re.compile(trie_pattern(forms))
def candidates(raw):
 out=set()
 variants=[raw]
 for pos,ch in enumerate(raw):
  if ch in '!@#$%&?~':
   for length in range(5,8):
    for start in range(max(0,pos-length+1),pos+1):
     chunk=raw[start:start+length]
     if re.fullmatch(r'(?:[A-P]{2}[!#$&][0-9]{3}|[A-P]{3}[!$][0-9]{2}|[0-9]{3}[%?][A-P]{3}|[A-P]{2}[0-9]{2}[%?][A-P]|[0-9]{2}[%?][A-P]{2}[a-z0-9]|[a-z0-9]{3}[&#@~][A-P]{2,3}|[@~][A-P]{2}[a-z0-9]{3}|[A-P]{2}[@~][A-P]{3}|[A-P][!$][a-z0-9]{3}[A-P])',chunk): variants.append(raw[:start]+raw[start+length:])
 for v in variants:
  end=re.search(r':(?:join|ctx|key|raw|doc|slot|id)[a-p]{3}|(?<!=)[)\]>}][a-p]{3}',v)
  if end: v=v[:end.start()]
  else:
   tails=list(re.finditer(r'[a-p]{3}(?:::|~~|--|__|=>|\+\+|[#$%|/@~])',v))
   if tails: v=v[:tails[-1].start()]
  for m in pattern.finditer(norm(v)):
   if m.start()>0 and norm(v)[m.start()-1].isdigit(): continue
   if m.end()!=len(norm(v)): continue
   out.update(forms[m.group()])
 return sorted(out)
check=con.read_parquet('/workspace/data/kev_db/kev_entries.parquet')
for row in check.filter(check.known_ransomware_use=='Known').select('cve_ref','notes').to_pyarrow().to_pylist():
 cid=re.search(r'nvd\.nist\.gov/vuln/detail/(CVE-[0-9]{4}-[0-9]+)',row['notes'])[1]
 assert cid in candidates(row['cve_ref']), (cid,row['cve_ref'])
rows=s.mutate(score=s.score_text.re_extract(r'([0-9]+(?:\.[0-9]+)?)',1).cast('float64')).to_pyarrow().to_pylist()
matches=[]; ambiguous=[]
for row in rows:
 ids=candidates(row['cve_id'])
 if len(ids)>1: ambiguous.append((row,ids))
 for cid in ids: matches.append({'cid':cid,'score':row['score']})

print('matches',len(matches),'keys',keys[:3], 'ambiguous',len(ambiguous),ambiguous[:3])
m=ibis.memtable(__import__('pyarrow').Table.from_pylist(matches)).group_by('cid').aggregate(score=ibis._.score.max())
# Severity evidence is carried by the English descriptions; missing English
# descriptions cannot supply a severity classification for this task.
docs=con.read_parquet('/workspace/data/descriptions_db/cve_documents.parquet')
decoded_docs=[]
for row in docs.select('cve','descriptions').to_pyarrow().to_pylist():
 for cid in candidates(row['cve']):
  descriptions=json.loads(row['descriptions'] or '[]')
  decoded_docs.append({'cid':cid,'has_english':any(x.get('lang')=='en' and x.get('value') for x in descriptions)})
e=ibis.memtable(__import__('pyarrow').Table.from_pylist(decoded_docs)).group_by('cid').aggregate(has_english=ibis._.has_english.any())
m=m.join(e,'cid').filter(ibis._.has_english)
r=k.left_join(m,'cid').group_by('canonical_vendor').aggregate(total=ibis._.cid.nunique(),critical=(ibis._.score>=9).sum().fill_null(0),missing=ibis._.score.isnull().sum())
r=r.filter(r.total>=3).order_by(ibis.desc('critical')).to_pyarrow().to_pylist()
print(json.dumps(r,indent=2))
Path('/workspace/work/diagnostics.json').write_text(json.dumps(r))
winner=r[0]
assert winner['critical'] > r[1]['critical'], 'Top count is tied'
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':winner['canonical_vendor']}))
