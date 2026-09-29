import pandas as pd
import re, unicodedata, json
from difflib import SequenceMatcher
from collections import defaultdict
def ratio(a,b):
    return 100*SequenceMatcher(None,a,b,autojunk=False).ratio()
from pathlib import Path
OUT=Path('/workspace/work')
t=pd.read_parquet('/workspace/data/tracks/tracks.parquet').fillna('')
s=pd.read_parquet('/workspace/data/sales/sales.parquet')
def norm(x):
    return re.sub(r'[^\w]', '', unicodedata.normalize('NFKD',str(x)).casefold())
def parse(r):
    title,artist,album=str(r.title),str(r.artist),str(r.album)
    if r.source_id==1:
        # This source appends the album in parentheses.
        if ' (' in title: title=title.rsplit(' (',1)[0]
        elif '(' in title: title=title.split('(',1)[0]
    elif r.source_id==2:
        if ' - ' in title: artist,title=title.split(' - ',1)
    elif r.source_id==3:
        if ' - ' in title: title,album=title.split(' - ',1)
    elif r.source_id==4:
        title=re.sub(r'^\w{1,3}-','',title)
        album=re.sub(r'\s*\([^()]*\)$','',album)
    return pd.Series([title,artist,album,norm(title),norm(artist),norm(album)])
t[['song','performer','release','nt','na','nal']]=t.apply(parse,axis=1)
parent=list(range(len(t)))
def root(i):
    while parent[i]!=i:
        parent[i]=parent[parent[i]];i=parent[i]
    return i
def union(i,j):
    a,b=root(i),root(j)
    if a!=b: parent[b]=a
# Attribute matching ignores formatting and allows minor transcription errors.
rows=t.to_dict('records')
keys=(t.nt+'|'+t.na).tolist()
pairs=[]
blocks=defaultdict(set)
for i,r in enumerate(rows):
    for col in ['nt','na','nal']:
        v=r[col]
        if len(v)>=4:
            for part in [v[:5],v[-5:]]: blocks[(col,part)].add(i)
for i,k in enumerate(keys):
    if not rows[i]['nt']: continue
    candidates=set()
    for col in ['nt','na','nal']:
        v=rows[i][col]
        if len(v)>=4:
            for part in [v[:5],v[-5:]]: candidates.update(blocks[(col,part)])
    for j in candidates:
        if j<=i: continue
        a,b=rows[i],rows[j]
        ts=ratio(a['nt'],b['nt']); ars=ratio(a['na'],b['na'])
        als=ratio(a['nal'],b['nal']) if a['nal'] and b['nal'] else 0
        ok=(ts>=88 and ars>=88 and a['na'] and b['na']) or (ts>=94 and als>=90 and (not a['na'] or not b['na'])) or (ts>=80 and ars>=95 and als>=90) or (ts>=95 and ars>=80 and als>=90)
        if ok:
            union(i,j); pairs.append((i,j,ts,ars,als))
t['entity']=[root(i) for i in range(len(t))]
z=s.merge(t[['track_id','entity']],on='track_id',validate='many_to_one')
rank=z.groupby('entity').revenue_usd.sum().sort_values(ascending=False)
t['revenue']=t.track_id.map(s.groupby('track_id').revenue_usd.sum()).fillna(0)
t.to_csv(OUT/'resolved_tracks.csv',index=False)
rank.to_csv(OUT/'revenue_ranking.csv')
for entity,rev in rank.head(12).items():
    print('\nTOTAL',rev); print(t.loc[t.entity==entity,['track_id','source_id','title','artist','album','year','length','song','performer','revenue']].to_string(index=False))
best=t[t.entity==rank.index[0]]
# Prefer the source storing clean, separate attributes.
r=best.sort_values('source_id',ascending=False).iloc[0]
answer=f'“{r.song}” by {r.performer} generated the highest total revenue: ${rank.iloc[0]:,.2f} USD.'
(OUT/'answer.json').write_text(json.dumps({'answer':answer},ensure_ascii=False))
