import io,json,re,zipfile,posixpath
import xml.etree.ElementTree as ET
from pathlib import Path
import ibis
import pyarrow as pa
import pyarrow.parquet as pq

OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
assets=con.read_parquet('/workspace/data/domain_assets/files.parquet')
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
records=[]
for asset in assets.filter(assets.file_description.lower().contains('1-s2')).to_pyarrow().to_pylist():
    z=zipfile.ZipFile(io.BytesIO(asset['content']))
    book=ET.fromstring(z.read('xl/workbook.xml'))
    for sheet in book.findall('m:sheets/m:sheet',ns):
        if sheet.get('name')!='UCEC_CPTAC3_meta_table_V2.1': continue
        rid=sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        target=next(r.get('Target') for r in rels if r.get('Id')==rid)
        path=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
        strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rows=[]
        for row in ET.fromstring(z.read(path)).findall('.//m:sheetData/m:row',ns):
            vals={}
            for cell in row:
                if not cell.tag.endswith('}c'): continue
                v=cell.findtext('m:v',default='',namespaces=ns)
                if cell.get('t')=='s':v=strings[int(v)]
                elif cell.get('t')=='inlineStr':v=''.join(cell.find('m:is',ns).itertext())
                vals[re.sub(r'\d','',cell.get('r'))]=v
            rows.append(vals)
        headers={col:name for col,name in rows[0].items() if name}
        records.extend({name:row.get(col) for col,name in headers.items()} for row in rows[1:])
pq.write_table(pa.Table.from_pylist(records),OUT/'metadata.parquet')
meta=con.read_parquet(OUT/'metadata.parquet')
eligible=meta.filter(meta.Histologic_type.lower()=='serous',meta.Case_excluded.lower()=='no').mutate(age=meta.Age.try_cast('int64'))
oldest=eligible.filter(eligible.age==eligible.age.max()).select('idx','Proteomics_Participant_ID','age').distinct()
print('Oldest:',oldest.to_pyarrow().to_pylist())
docs=con.read_parquet('/workspace/data/domain_docs/files.parquet')
selected=docs.filter(docs.content.contains('respectively'))
pairs=[]
for doc in selected.to_pyarrow().to_pylist():
    for line in doc['content'].splitlines():
        m=re.match(r'(?:patients )?(.+?) (?:were hyperactivated with|showed elevated activity for|had proteins|expressed) (.+?), respectively',line)
        if not m:continue
        ids=m[1].split(', '); proteins=m[2].split(', ')
        assert len(ids)==len(proteins)
        pairs.extend({'patient':p.strip(),'protein':v.strip()} for p,v in zip(ids,proteins))
assert pairs
pq.write_table(pa.Table.from_pylist(pairs),OUT/'biomarkers.parquet')
bio=con.read_parquet(OUT/'biomarkers.parquet')
def canonical(col):
    s=col.upper().re_replace('[^A-Z0-9]','')
    return s.re_extract('^([A-Z]+)',1)+s.re_extract('([0-9]+)$',1).cast('int64').cast('string')
bio=bio.mutate(key=canonical(bio.patient))
oldest=oldest.mutate(key=canonical(oldest.idx))
result=oldest.join(bio,'key').select('idx','age','protein').distinct().to_pyarrow().to_pylist()
print('Matched:',result)
assert result
proteins=sorted({r['protein'] for r in result})
assert len(proteins)==1,proteins
(OUT/'answer.json').write_text(json.dumps({'answer':proteins[0]}))
