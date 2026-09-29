import polars as pl
import re, unicodedata, json
from difflib import SequenceMatcher
def ratio(a,b): return 100 * SequenceMatcher(None,a,b).ratio() if a and b else 0
from collections import defaultdict

def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s or '').casefold() if c.isalnum())
def clean(r):
    t,a,b = r['title'] or '',r['artist'] or '',r['album'] or ''
    src=r['source_id']
    if src==2 and ' - ' in t: a,t=t.split(' - ',1)
    if src==3 and ' - ' in t: t,b=t.rsplit(' - ',1)
    if src==4:
        t=re.sub(r'^\d+\s*-\s*','',t)
        b=re.sub(r'\s*\((?:\d{4}|unknown)\)$','',b)
    if src==1 and t.endswith(')'):
        pos=t.rfind(' (')
        if pos>=0 and ratio(norm(t[pos+2:-1]),norm(b))>80: t=t[:pos]
        elif norm(b) and norm(t).endswith(norm(b)):
            # Accommodate missing spaces in the title/album decoration.
            for i,c in enumerate(t):
                if c=='(' and norm(t[i+1:-1])==norm(b): t=t[:i];break
    return {'track_id':r['track_id'],'song_title':t,'song_artist':a,'nt':norm(t),'na':norm(a),'nb':norm(b)}

tracks=pl.read_parquet('/workspace/data/tracks/tracks.parquet')
sales=pl.read_parquet('/workspace/data/sales/sales.parquet')
x=pl.DataFrame([clean(r) for r in tracks.iter_rows(named=True)])
rows=x.to_dicts(); parent=list(range(len(rows)))
def root(i):
    while parent[i]!=i: parent[i]=parent[parent[i]];i=parent[i]
    return i
def union(i,j):parent[root(i)]=root(j)
blocks=defaultdict(list)
for i,r in enumerate(rows):
    if r['nt'] and r['na']:blocks[(r['nt'],r['na'])].append(i)
for ids in blocks.values():
    for i in ids[1:]:union(ids[0],i)
# Compare within exact artist or title blocks to identify misspellings.
for fields in [('na',),('nt',),('nb',)]:
    blocks=defaultdict(list)
    for i,r in enumerate(rows):
        key=tuple(r[f] for f in fields)
        if all(key):blocks[key].append(i)
    for ids in blocks.values():
        for p,i in enumerate(ids):
            a=rows[i]
            for j in ids[p+1:]:
                b=rows[j]
                ts=ratio(a['nt'],b['nt']); ars=ratio(a['na'],b['na']); bs=ratio(a['nb'],b['nb'])
                if (ts>=90 and ars>=90 and (bs>=80 or ts==100 or ars==100)) or (ts>=85 and ars>=85 and bs>=90):union(i,j)
                elif ts==100 and bs>=95 and (not a['na'] or not b['na']):union(i,j)
mapping=x.with_columns(pl.Series('entity',[root(i) for i in range(len(rows))]))
ranking=sales.join(mapping,on='track_id').group_by('entity').agg(pl.col('revenue_usd').sum(),pl.col('track_id').n_unique().alias('records')).sort('revenue_usd',descending=True)
ranking.join(mapping.unique('entity'),on='entity').sort('revenue_usd',descending=True).head(30).write_csv('/workspace/work/ranking.csv')
winner=ranking.row(0,named=True)
members=mapping.filter(pl.col('entity')==winner['entity'])
tracks.join(members.select('track_id'),on='track_id').write_csv('/workspace/work/winner_records.csv')
label=members.group_by('song_title','song_artist').len().sort('len',descending=True).row(0,named=True)
answer=f"{label['song_title']} by {label['song_artist']} generated the highest total revenue: ${winner['revenue_usd']:,.2f} USD."
with open('/workspace/work/answer.json','w') as f:json.dump({'answer':answer},f)
print(answer)
