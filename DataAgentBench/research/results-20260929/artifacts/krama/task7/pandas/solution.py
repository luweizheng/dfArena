import io,json,re,zipfile,posixpath
import xml.etree.ElementTree as ET
import pandas as pd

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sheet_frame(blob, sheet_name):
    z=zipfile.ZipFile(io.BytesIO(blob))
    wb=ET.fromstring(z.read('xl/workbook.xml'))
    sheet=next((s for s in wb.find('m:sheets',NS) if s.get('name')==sheet_name),None)
    if sheet is None:return None
    rid=sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    target=next(r.get('Target') for r in rels if r.get('Id')==rid)
    path=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        strings=[''.join(t.text or '' for t in s.iter('{'+NS['m']+'}t')) for s in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    rows=[]
    for row in ET.fromstring(z.read(path)).findall('.//m:sheetData/m:row',NS):
        vals={}
        for c in row:
            col=re.sub(r'\d','',c.get('r'))
            v=c.findtext('m:v',default='',namespaces=NS)
            if c.get('t')=='s':v=strings[int(v)]
            elif c.get('t')=='inlineStr':v=''.join(c.itertext())
            vals[col]=v
        rows.append(vals)
    frame=pd.DataFrame(rows[1:]).rename(columns=rows[0])
    return frame

def canonical(value):
    m=re.fullmatch(r'([A-Za-z]+)[\s._/-]*0*(\d+)',str(value).strip())
    if not m:raise ValueError(value)
    return m[1].upper()+str(int(m[2]))

assets=pd.read_parquet('/workspace/data/domain_assets/files.parquet')
frames=[]
for blob in assets.loc[assets.file_description.str.contains('1-s2',na=False),'content']:
    frame=sheet_frame(blob,'UCEC_CPTAC3_meta_table_V2.1')
    if frame is not None:frames.append(frame)
assert len(frames)==1
patients=frames[0]
patients['patient']=patients['idx'].map(canonical)
patients['Age']=pd.to_numeric(patients['Age'],errors='coerce')
docs=pd.read_parquet('/workspace/data/domain_docs/files.parquet')
pairs=[]
pattern=r'^(?:patients\s+)?(.+?) (?:were hyperactivated with|had proteins|expressed|showed elevated activity for) (.+?), respectively$'
for doc in docs.content:
    for line in doc.splitlines():
        if 'respectively' not in line:continue
        m=re.match(pattern,line.split('\t')[0])
        if not m:continue
        ids=[s.strip() for s in m[1].split(',')]
        proteins=[s.strip() for s in m[2].split(',')]
        assert len(ids)==len(proteins)
        pairs.extend((canonical(i),p) for i,p in zip(ids,proteins))
bio=pd.DataFrame(pairs,columns=['patient','protein']).drop_duplicates()
selected=patients.merge(bio.loc[bio.protein.eq('CDK12'),['patient']].drop_duplicates(),on='patient',how='inner')
assert len(selected)>0
assert not selected.patient.duplicated().any()
selected[['patient','Age']].to_csv('/workspace/work/selected_patients.csv',index=False)
answer=f'{selected.Age.mean():.2f} years'
with open('/workspace/work/answer.json','w') as f:json.dump({'answer':answer},f)
print(selected[['patient','Age']].to_string(index=False))
print('Count:',len(selected),'Mean:',answer)
