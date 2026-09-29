import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
SHEET = 'UCEC_CPTAC3_meta_table_V2.1'

# Decode spreadsheet cells using the standard library, then compute with Polars.
frames = []
for description, blob in pl.read_parquet(DATA / 'domain_assets/files.parquet').iter_rows():
    if not blob.startswith(b'PK'):
        continue
    z = zipfile.ZipFile(io.BytesIO(blob))
    if 'xl/workbook.xml' not in z.namelist():
        continue
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    sheets = [s for s in wb.findall('s:sheets/s:sheet', NS) if s.get('name') == SHEET]
    if not sheets:
        continue
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rid = sheets[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    target = next(r.get('Target') for r in rels if r.get('Id') == rid)
    path = target.lstrip('/') if target.startswith('/') else 'xl/' + target
    strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        strings = [''.join(t.text or '' for t in si.findall('.//s:t', NS)) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
    rows = []
    for row in ET.fromstring(z.read(path)).findall('.//s:sheetData/s:row', NS):
        values = {}
        for cell in row:
            col = re.sub(r'\d', '', cell.get('r'))
            value = cell.findtext('s:v', default=None, namespaces=NS)
            if cell.get('t') == 's' and value is not None:
                value = strings[int(value)]
            elif cell.get('t') == 'inlineStr':
                value = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
            values[col] = value
        rows.append(values)
    headers = rows[0]
    frames.append(pl.DataFrame([{headers[k]: v for k, v in row.items() if k in headers} for row in rows[1:]], infer_schema_length=None))
assert len(frames) == 1
meta = frames[0]

# Each prose row gives parallel lists of patient IDs and hyperactivated proteins.
pairs = []
for content in pl.read_parquet(DATA / 'domain_docs/files.parquet')['content']:
    for line in content.splitlines():
        if 'respectively' not in line:
            continue
        match = re.fullmatch(r'(?:patients )?(.+?) (?:were hyperactivated with|had proteins|expressed|showed elevated activity for) (.+?), respectively\s*', line.split('\t')[0])
        if not match:
            continue
        ids, proteins = ([v.strip() for v in group.split(',')] for group in match.groups())
        assert len(ids) == len(proteins)
        pairs.extend(zip(ids, proteins))
protein = pl.DataFrame(pairs, schema=['patient', 'protein'], orient='row')
def canonical(col):
    cleaned = pl.col(col).str.to_uppercase().str.replace_all(r'[^A-Z0-9]', '')
    return pl.concat_str(cleaned.str.extract(r'^([A-Z]+)', 1), cleaned.str.extract(r'(\d+)$', 1).cast(pl.Int64).cast(pl.String))
selected = protein.filter(pl.col('protein') == 'CDK12').with_columns(canonical('patient').alias('key')).select('key').unique()
matched = meta.with_columns(canonical('idx').alias('key'), pl.col('Age').cast(pl.Float64, strict=False)).join(selected, on='key', how='semi')
matched.select('idx', 'Age').write_csv(OUT / 'matched_patients.csv')
mean = matched.select(pl.col('Age').mean()).item()
assert mean is not None
print(matched.select('idx', 'Age'))
print('Patients:', matched.height, 'Known ages:', matched['Age'].count(), 'Average:', mean)
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{mean:.2f} years'}))
