import io, json, re, zipfile, posixpath
import xml.etree.ElementTree as ET
from pathlib import Path
import polars as pl

OUT=Path('/workspace/work')
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
assets=pl.read_parquet('/workspace/data/domain_assets/files.parquet')
frames=[]
for blob in assets.filter(pl.col('file_description').str.contains('1-s2'))['content']:
    z=zipfile.ZipFile(io.BytesIO(blob))
    wb=ET.fromstring(z.read('xl/workbook.xml'))
    for sheet in wb.findall('m:sheets/m:sheet',NS):
        if sheet.get('name')!='UCEC_CPTAC3_meta_table_V2.1': continue
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rid=sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        target=next(r.get('Target') for r in rels if r.get('Id')==rid)
        path=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
        strings=[''.join(t.text or '' for t in si.findall('.//m:t',NS)) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rows=[]
        for row in ET.fromstring(z.read(path)).findall('.//m:sheetData/m:row',NS):
            vals={}
            for c in row:
                col=re.sub(r'\d','',c.get('r'))
                v=c.findtext('m:v',default='',namespaces=NS)
                vals[col]=strings[int(v)] if c.get('t')=='s' else v
            rows.append(vals)
        headers=rows[0]
        frames.append(pl.DataFrame([{name:r.get(col) for col,name in headers.items()} for r in rows[1:]]))
meta=pl.concat(frames).with_columns(pl.col('Age').cast(pl.Float64,strict=False))
eligible=meta.filter((pl.col('Histologic_type')=='Serous') & (pl.col('Case_excluded')=='No'))
oldest=eligible.filter(pl.col('Age')==pl.col('Age').max()).select('idx','Proteomics_Participant_ID','Age').unique()

def canon(s):
    s=re.sub(r'[^A-Z0-9]','',s.upper())
    m=re.fullmatch(r'([A-Z]+)0*(\d+)',s)
    return m[1]+str(int(m[2])) if m else s

records=[]
docs=pl.read_parquet('/workspace/data/domain_docs/files.parquet')
pattern=re.compile(r'^(?:patients )?(.+?) (?:were hyperactivated with|had proteins|showed elevated activity for|expressed) (.+?), respectively')
for doc in docs['content']:
    for line in doc.splitlines():
        m=pattern.match(line)
        if not m: continue
        ids=[x.strip() for x in m[1].split(',')]
        proteins=[x.strip() for x in m[2].split(',')]
        assert len(ids)==len(proteins)
        records.extend({'key':canon(i),'protein':p} for i,p in zip(ids,proteins))
proteins=pl.DataFrame(records)
result=oldest.with_columns(pl.col('idx').map_elements(canon,return_dtype=pl.String).alias('key')).join(proteins,on='key',how='left').unique()
assert result['protein'].null_count()==0
answers=result['protein'].unique().to_list()
assert len(answers)==1
eligible.select('idx','Age').sort('Age',descending=True).write_csv(OUT/'eligible_patients.csv')
result.write_csv(OUT/'oldest_patient_protein.csv')
(OUT/'answer.json').write_text(json.dumps({'answer':answers[0]}))
print(result)
print((OUT/'answer.json').read_text())
