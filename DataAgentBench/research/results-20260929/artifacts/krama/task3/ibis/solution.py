import json,re
from html.parser import HTMLParser
from pathlib import Path
import ibis
import pyarrow as pa
import pyarrow.parquet as pq

OUT=Path('/workspace/work')
class Tables(HTMLParser):
    def __init__(self):
        super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='table': self.table=[]
        elif tag=='tr' and self.table is not None: self.row=[]
        elif tag in ('td','th') and self.row is not None: self.cell=''
    def handle_data(self,data):
        if self.cell is not None:self.cell+=data
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(self.cell.strip());self.cell=None
        elif tag=='tr' and self.row is not None:
            self.table.append(self.row);self.row=None
        elif tag=='table' and self.table is not None:
            self.tables.append(self.table);self.table=None

c=ibis.duckdb.connect()
a=c.read_parquet('/workspace/data/domain_assets/files.parquet')
blob=a.filter(a.file_description.contains('metropolitan_statistics')).select('content').to_pyarrow().to_pylist()[0]['content']
h=Tables();h.feed(blob.decode('utf-8'))
poprows=[]
for tab in h.tables:
    if tab and tab[0][0].lower()=='metropolitan statistical area':
        for row in tab[1:]:
            poprows.append(dict(msa=row[0],p2024=int(row[1].replace(',','')),p2020=int(row[2].replace(',',''))))
pq.write_table(pa.Table.from_pylist(poprows),OUT/'population.parquet')
p=c.read_parquet(OUT/'population.parquet')
def key(x):
    return x.re_replace(r' (?:MSA|Metropolitan Statistical Area).*$', '').re_replace('[–—−]','-').re_replace('-+','-').lower().strip()
p=p.mutate(key=key(p.msa),p2023=p.p2020+(p.p2024-p.p2020)*0.75)
p=p.filter(p.p2023>1000000)
d=c.read_parquet('/workspace/data/domain_docs/files.parquet')
d=d.filter(d.content.contains('Metropolitan Area\tReport Summary'))
rows=[]
for doc in d.to_pyarrow().to_pylist():
    for line in doc['content'].splitlines():
        if '\t' in line and 'Statistical Area\t' in line:
            name,summary=line.split('\t',1); rows.append(dict(msa=name,summary=summary))
pq.write_table(pa.Table.from_pylist(rows),OUT/'reports.parquet')
t=c.read_parquet(OUT/'reports.parquet')
t=t.mutate(key=key(t.msa))
t=t.filter(t.summary.contains('2024'))
j=p.join(t,'key').select(p.msa,p.p2023,t.summary)
OUT.joinpath('selected.json').write_text(json.dumps(j.order_by(p.msa).to_pyarrow().to_pylist(),indent=2))
print('population',p.count().execute(),'joined',j.count().execute())
# Extract report counts (not per-capita rates) from the source prose in SQL.
num=r'[0-9]+(?:[, ][0-9]{3})*'
patterns=[
    rf'({num}) identity theft (?:reports|complaints|cases)',
    rf'identity theft rate of {num} per 100K \(({num}) total reports\)',
    rf'{num} and ({num}) (?:complaints|total reports|total filings|filed complaints|reports|underlying reports)',
    rf'(?:totaled|counts of|totals of|counts through .*? reached|complaint counts .*? were|complaint volumes .*?:) {num} and ({num})(?:,| \()',
]
values=[j.summary.re_extract(pat,1).nullif('').re_replace('[, ]','').cast('int64') for pat in patterns]
j=j.mutate(thefts=ibis.coalesce(*values))
missing=j.filter(j.thefts.isnull()).to_pyarrow().to_pylist()
assert not missing,missing
assert j.msa.nunique().execute()==j.count().execute(),'Multiple reports for an MSA'
j.order_by('msa').to_parquet(OUT/'matched_msas.parquet')
result=j.aggregate(n=j.count(),total=j.thefts.sum(),average=j.thefts.mean()).to_pyarrow().to_pylist()[0]
OUT.joinpath('answer.json').write_text(json.dumps({'answer':f"{result['average']:.4f}"})+'\n')
print(result)
