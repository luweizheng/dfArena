import ibis
import json
from pathlib import Path

OUT=Path('/workspace/work')
c=ibis.duckdb.connect()
docs=c.read_parquet('/workspace/data/domain_docs/files.parquet')
assets=c.read_parquet('/workspace/data/domain_assets/files.parquet')
lines=docs.filter(docs.content.contains('Metropolitan Area\tReport Summary')).select(line=docs.content.split('\n').unnest())
lines=lines.filter(lines.line.contains('2024') & lines.line.contains('Metropolitan Statistical Area\t'))
lines=lines.mutate(msa=lines.line.split('\t')[0], prose=lines.line.split('\t')[1])
# Number tokens permit comma or space thousands separators.
n=r'(\d+(?:[, ]\d{3})*)'
p=lines.prose
patterns=[
 (rf'{n} and {n} per(?:-| )100',2),
 (rf'[Pp]er-100K rates.*?were {n} and {n}',2),
 (rf'per-100K rates of {n} and {n}',2),
 (rf'per 100K.*?were {n} and {n}',2),
 (rf'rate/count pairs were {n}/{n} and {n}/{n}',3),
 (rf'identity theft (?:reports|cases) \({n}(?: per 100|/100)',1),
 (rf'identity theft complaints at {n} per 100',1),
 (rf'identity theft rate of {n} per 100',1),
 (rf'recorded {n} identity thefts and',1),
]
values=[p.re_extract(pat,idx).nullif('').re_replace('[, ]','').cast('int64') for pat,idx in patterns]
rate=ibis.coalesce(*values)
# In the reversed-order narrative the first of the two rates is identity theft.
reverse=p.re_search(r'filed .*identity theft reports and .*fraud reports')
first=p.re_extract(rf'at rates of {n} and {n}',1).nullif('').re_replace('[, ]','').cast('int64')
ranked=lines.mutate(rate=reverse.ifelse(first,rate))
assert ranked.filter(ranked.rate.isnull()).count().execute() == 0, 'Unparsed 2024 rate'
blob=assets.filter(assets.file_description.contains('metropolitan_statistics')).select('content').to_pyarrow().to_pylist()[0]['content']
(OUT/'metropolitan_statistics.html').write_bytes(blob)

from html.parser import HTMLParser
class Tables(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.row=None; self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr': self.row=[]
        if tag in ('th','td') and self.row is not None: self.cell=[]
    def handle_data(self,data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('th','td') and self.cell is not None:
            self.row.append(''.join(self.cell).strip()); self.cell=None
        if tag=='tr' and self.row is not None:
            self.rows.append(self.row); self.row=None
parser=Tables();parser.feed(blob.decode('utf-8'))
# HTML decoding is structural extraction; numeric conversion, matching,
# ranking, and population arithmetic remain lazy Ibis expressions.
records=[{'population_msa': r[0], 'pop2024_text': r[1], 'pop2020_text': r[2]}
         for r in parser.rows if len(r)==5 and r[0].endswith(' MSA')]
pop=ibis.memtable(records)
def key(col):
    return (col.re_replace(r' (Metropolitan Statistical Area|MSA)$', '')
            .re_replace('[–—-]+','-').lower().strip())
pop=pop.mutate(key=key(pop.population_msa),
               pop2024=pop.pop2024_text.replace(',','').cast('int64'),
               pop2020=pop.pop2020_text.replace(',','').cast('int64'))
top=ranked.order_by(ibis.desc('rate')).limit(1)
top=top.mutate(key=key(top.msa))
result=top.join(pop,'key').select(top.msa,top.rate,pop.pop2020,pop.pop2024,
                                change=(pop.pop2024-pop.pop2020).abs())
rows=result.to_pyarrow().to_pylist()
assert len(rows)==1, 'Population match must be unique'
r=rows[0]
(OUT/'evidence.json').write_text(json.dumps(r,indent=2))
answer=f"{r['change']:,} people."
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(json.dumps(r,indent=2))
