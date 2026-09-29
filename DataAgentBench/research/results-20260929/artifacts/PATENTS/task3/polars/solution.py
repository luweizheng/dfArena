import json
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
p = pl.read_parquet(ROOT/'publication/publicationinfo.parquet', columns=['Patents_info','cpc','citation']).with_row_index('row_id')
s = pl.col('Patents_info')
p = p.with_columns(
    pl.coalesce(s.str.extract(r'^(.*?) holds the ',1), s.str.extract(r'(?:owned by|assigned to|held by|belonging to) (.*?) and has ',1), s.str.extract(r'(?:owned by|assigned to|held by|belonging to) (.*?), with ',1)).alias('assignee'),
    s.str.extract(r'(?:publication number|publication no\.|pub\. number) ([^\s.]+)',1).alias('publication_number')
)
assert p['publication_number'].null_count() == 0
print('Unparsed assignees:', p.filter(pl.col('assignee').is_null()).height)
print(p.filter(pl.col('assignee').is_null()).select('Patents_info').head(10))
uc = p.filter(pl.col('assignee') == 'UNIV CALIFORNIA').select(pl.col('publication_number').alias('cited_publication')).unique()
# Extract only publication_number values, not publication identifiers appearing in NPL text.
edges = p.select('row_id', pl.col('citation').str.extract_all(r'"publication_number"\s*:\s*"[^"]+"').alias('cited_publication')).explode('cited_publication').with_columns(pl.col('cited_publication').str.extract(r':\s*"([^"]+)"',1)).join(uc,on='cited_publication',how='semi').unique()
citing = p.join(edges.select('row_id').unique(),on='row_id',how='semi').filter(pl.col('assignee') != 'UNIV CALIFORNIA')
assert citing['assignee'].null_count() == 0
primary = citing.with_columns(pl.col('cpc').str.json_decode(pl.List(pl.Struct({'code':pl.String,'first':pl.Boolean}))).alias('primary')).explode('primary').filter(pl.col('primary').struct.field('first') == True).with_columns(pl.col('primary').struct.field('code').str.slice(0,4).alias('symbol'))
definitions = pl.read_parquet(ROOT/'CPCDefinition/cpc_definition.parquet',columns=['symbol','titleFull']).unique()
result = primary.select('assignee','symbol').unique().join(definitions,on='symbol',how='left').unique().sort('assignee','symbol')
assert result['titleFull'].null_count() == 0
result.write_csv(OUT/'assignee_subclasses.csv')
edges.join(p.select('row_id','publication_number','assignee'),on='row_id').write_csv(OUT/'citation_evidence.csv')
lines=[]
for group in result.partition_by('assignee',maintain_order=True):
    lines.append(group['assignee'][0] + ': ' + '; '.join(f'{r["symbol"]} — {r["titleFull"]}' for r in group.iter_rows(named=True)))
answer = '\n'.join(lines)
(OUT/'answer.json').write_text(json.dumps({'answer':answer},ensure_ascii=False,indent=2)+'\n')
print('UC publications:',uc.height,'Citing patents:',citing.height,'Assignees:',result['assignee'].n_unique(),'Pairs:',result.height)
print(answer)
