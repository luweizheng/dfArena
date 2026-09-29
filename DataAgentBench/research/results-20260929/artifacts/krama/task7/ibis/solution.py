import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import ibis
import pyarrow as pa

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
assets = con.read_parquet('/workspace/data/domain_assets/files.parquet')
docs = con.read_parquet('/workspace/data/domain_docs/files.parquet')
ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
patients = []
# Decode the binary workbook representation, then use Ibis for relational work.
for asset in assets.filter(assets.file_description.contains('1-s2')).to_pyarrow().to_pylist():
    z = zipfile.ZipFile(io.BytesIO(asset['content']))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    for sheet in wb.findall('s:sheets/s:sheet', ns):
        if sheet.attrib['name'] != 'UCEC_CPTAC3_meta_table_V2.1':
            continue
        rid = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        target = next(r.attrib['Target'] for r in rels if r.attrib['Id'] == rid)
        path = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rows = []
        for row in ET.fromstring(z.read(path)).findall('.//s:row', ns):
            record = {}
            for cell in row:
                col = re.sub(r'\d', '', cell.attrib['r'])
                value = cell.findtext('s:v', default='', namespaces=ns)
                if cell.attrib.get('t') == 's':
                    value = strings[int(value)]
                record[col] = value
            rows.append(record)
        headers = rows[0]
        id_col = next(k for k, v in headers.items() if v == 'idx')
        age_col = next(k for k, v in headers.items() if v == 'Age')
        patients.extend({'patient': r.get(id_col), 'age_text': r.get(age_col)} for r in rows[1:])
assert patients

assignments = []
pattern = re.compile(r'^(?:patients )?(.+?) (?:were hyperactivated with|had proteins|showed elevated activity for|expressed) (.+?), respectively$')
for doc in docs.filter(docs.content.contains('CDK12')).to_pyarrow().to_pylist():
    for line in doc['content'].splitlines():
        if '\t' not in line or 'respectively' not in line:
            continue
        prose = line.split('\t')[0]
        match = pattern.fullmatch(prose)
        assert match, prose
        ids = match[1].split(', ')
        proteins = match[2].split(', ')
        assert len(ids) == len(proteins)
        assignments.extend({'patient': pid, 'protein': protein} for pid, protein in zip(ids, proteins))

ibis.set_backend(con)
p = ibis.memtable(pa.Table.from_pylist(patients))
b = ibis.memtable(pa.Table.from_pylist(assignments))
def canonical(expr):
    clean = expr.upper().re_replace('[^A-Z0-9]', '')
    return clean.re_extract('^([A-Z]+)', 1) + clean.re_extract('([0-9]+)$', 1).cast('int64').cast('string')
p = p.mutate(key=canonical(p.patient), age=p.age_text.try_cast('float64'))
b = b.mutate(key=canonical(b.patient))
selected = p.semi_join(b.filter(b.protein == 'CDK12'), 'key')
result = selected.aggregate(average_age=selected.age.mean(), patients=selected.count(), valid_ages=selected.age.count()).to_pyarrow().to_pylist()[0]
assert result['valid_ages'] > 0
selected.select('patient', 'age').order_by('patient').to_pyarrow().to_pydict()
(OUT / 'matched_patients.json').write_text(json.dumps(selected.select('patient','age').order_by('patient').to_pyarrow().to_pylist(), indent=2))
(OUT / 'answer.json').write_text(json.dumps({'answer': f"{result['average_age']:.2f} years"}))
print(result)
