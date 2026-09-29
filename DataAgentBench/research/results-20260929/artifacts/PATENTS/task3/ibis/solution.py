import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
con.raw_sql("SET temp_directory='/workspace/work/duckdb_tmp'")
p = con.read_parquet('/workspace/data/publication/publicationinfo.parquet')
d = con.read_parquet('/workspace/data/CPCDefinition/cpc_definition.parquet')
s = p.Patents_info
assignee = ibis.coalesce(
    s.re_extract(r'^(.*?) holds the ', 1).nullif(''),
    s.re_extract(r'(?:owned by|assigned to|belonging to|held by) (.*?) and has ', 1).nullif(''),
    s.re_extract(r'(?:owned by|assigned to|belonging to|held by) (.*?), with ', 1).nullif(''),
)
pub = s.re_extract(r'(?:publication number|publication no\.|pub\. number) ([A-Za-z0-9-]+)', 1)
p = p.select(assignee=assignee, publication=pub, cpc=p.cpc, citation=p.citation)
missing = p.filter(p.assignee.isnull() | (p.publication == '')).select('assignee','publication').count().execute()
assert missing == 0, f'Unparsed summaries: {missing}'
uc = p.filter(p.assignee == 'UNIV CALIFORNIA').select(cited_publication=p.publication).distinct()
others = p.filter(p.assignee != 'UNIV CALIFORNIA')
refs = others.select('assignee', 'publication', 'cpc', ref=others.citation.cast('json').cast('array<struct<application_number: string, category: string, filing_date: int64, npl_text: string, publication_number: string, type: string>>').unnest())
refs = refs.mutate(cited_publication=refs.ref.publication_number)
citing = refs.semi_join(uc, 'cited_publication').select('assignee','publication','cpc').distinct()
primary = citing.select('assignee', entry=citing.cpc.cast('json').cast('array<struct<code: string, first: boolean, inventive: boolean, tree: json>>').unnest())
primary = primary.filter(primary.entry['first']).select('assignee', subclass=primary.entry.code.substr(0,4)).distinct()
result = primary.left_join(d, primary.subclass == d.symbol).select(primary.assignee, primary.subclass, d.titleFull).distinct().order_by('assignee','subclass')
rows = result.to_pyarrow().to_pylist()
assert all(r['titleFull'] is not None for r in rows), 'Missing CPC subclass titles'
(OUT / 'results.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False))
answer = '\n'.join(f"{r['assignee']} — {r['subclass']}: {r['titleFull']}" for r in rows)
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False))
print(f'{len(rows)} assignee/subclass pairs; {len(set(r["assignee"] for r in rows))} assignees')
print(answer)
