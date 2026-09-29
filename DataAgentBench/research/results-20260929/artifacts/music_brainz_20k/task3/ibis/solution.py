import json, re, unicodedata
from collections import defaultdict
from pathlib import Path
import ibis
from difflib import SequenceMatcher
def ratio(a,b):
    return 100 * SequenceMatcher(None,a,b,autojunk=False).ratio()

OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
t=con.read_parquet('/workspace/data/tracks/tracks.parquet')
s=con.read_parquet('/workspace/data/sales/sales.parquet')
# Decode the five source-specific representations before entity matching.
name=ibis.cases((t.source_id==2,t.title.re_extract(r'^(.+?) - ',1)),else_=t.artist)
title=ibis.cases((t.source_id==2,t.title.re_replace(r'^.+? - ','')),(t.source_id==3,t.title.re_replace(r' - .*$', '')),(t.source_id==4,t.title.re_replace(r'^\d+\s*-\s*','')),(t.source_id==1,t.title.re_replace(r'\s*\(.*$', '')),else_=t.title)
album=ibis.cases((t.source_id==3,t.title.re_extract(r' - (.*)$',1)),(t.source_id==4,t.album.re_replace(r'\s*\((?:\d{4}|unknown)\)$','')),else_=t.album)
n=t.mutate(song_title=title,song_artist=name,song_album=album)
rows=n.to_pyarrow().to_pylist()
def norm(x):
    x=unicodedata.normalize('NFKD',x or '').casefold()
    x=''.join(c for c in x if c.isalnum())
    return '' if x in {'unknown','na','none','null','unk'} else x

def duration(r):
    x=(r['length'] or '').replace(' ','')
    try:
        if r['source_id']==1:
            m,se=x.split(':'); return float(m)*60+float(se)
        if r['source_id']==4:
            m,se=re.match(r'(\d+)m(\d+)sec',x).groups(); return float(m)*60+float(se)
        v=float(x)
        return v/1000 if r['source_id']==5 else v*60 if r['source_id']==3 else v
    except (ValueError,AttributeError): return None
for r in rows:
    r['nt']=norm(r['song_title']);r['na']=norm(r['song_artist']);r['nb']=norm(r['song_album']);r['dur']=duration(r)
parent=list(range(len(rows)))
def root(i):
    while parent[i]!=i:
        parent[i]=parent[parent[i]];i=parent[i]
    return i
def union(i,j):
    a,b=root(i),root(j)
    if a!=b:parent[max(a,b)]=min(a,b)
blocks=defaultdict(list)
for i,r in enumerate(rows):
    for f in ['nt','na','nb']:
        if r[f]:blocks[(f,r[f])].append(i)
seen=set();matches=[]
for ids in blocks.values():
    for pos,i in enumerate(ids):
        a=rows[i]
        for j in ids[pos+1:]:
            if (i,j) in seen:continue
            seen.add((i,j));b=rows[j]
            ts=ratio(a['nt'],b['nt']) if a['nt'] and b['nt'] else 0
            ars=ratio(a['na'],b['na']) if a['na'] and b['na'] else 0
            als=ratio(a['nb'],b['nb']) if a['nb'] and b['nb'] else 0
            close=a['dur'] is not None and b['dur'] is not None and abs(a['dur']-b['dur'])<=3
            match=(ts>=90 and ars>=90) or (ts>=90 and als>=90 and (ars>=65 or not a['na'] or not b['na'])) or (ars>=92 and als>=92 and close and (ts>=65 or not a['nt'] or not b['nt']))
            if match:
                union(i,j); matches.append((a['track_id'],b['track_id'],ts,ars,als))
mapping=ibis.memtable({'track_id':[r['track_id'] for r in rows], 'entity_id':[root(i) for i in range(len(rows))]})
joined=s.join(mapping,'track_id')
ranked=joined.group_by('entity_id').aggregate(total_revenue=joined.revenue_usd.cast('decimal(18,2)').sum(),record_count=joined.track_id.nunique()).order_by(ibis.desc('total_revenue'))
top=ranked.limit(20).to_pyarrow().to_pylist()
details=[]
for item in top:
    members=[r for i,r in enumerate(rows) if root(i)==item['entity_id']]
    details.append({**item,'members':members})
(OUT/'ranking.json').write_text(json.dumps(details,ensure_ascii=False,default=str,indent=2))
winner=top[0];members=details[0]['members']
# Prefer a complete, unwrapped source record to label the winning entity.
label=max(members,key=lambda r:(bool(r['song_title']) and bool(r['song_artist']),r['source_id']==5,len(r['song_title'] or '')))
answer=f"{label['song_title']} by {label['song_artist']} generated the highest total revenue: ${winner['total_revenue']:,.2f} USD."
(OUT/'answer.json').write_text(json.dumps({'answer':answer},ensure_ascii=False))
print(answer)
print('Matched pairs:',len(matches))
print(json.dumps(details[:5],ensure_ascii=False,default=str,indent=2))
