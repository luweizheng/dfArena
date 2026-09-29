import io,json,re,zipfile,posixpath
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
SHEET='UCEC_CPTAC3_meta_table_V2.1'
def read_sheet(blob):
    z=zipfile.ZipFile(io.BytesIO(blob))
    sheets=ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS)
    match=next((s for s in sheets if s.get('name')==SHEET),None)
    if match is None:return None
    rid=match.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    target=next(r.get('Target') for r in rels if r.get('Id')==rid)
    path=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        strings=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    rows=[]
    for row in ET.fromstring(z.read(path)).findall('.//s:sheetData/s:row',NS):
        d={}
        for c in row:
            col=re.match('[A-Z]+',c.get('r')).group();v=c.find('s:v',NS)
            value=v.text if v is not None else ''
            if c.get('t')=='s':value=strings[int(value)]
            if c.get('t')=='inlineStr':value=''.join(c.find('s:is',NS).itertext())
            d[col]=value
        rows.append(d)
    raw=pd.DataFrame(rows).fillna('')
    raw.columns=raw.iloc[0];return raw.iloc[1:].reset_index(drop=True)
def main():
    assets=pd.read_parquet('/workspace/data/domain_assets/files.parquet')
    frames=[]
    for blob in assets.loc[assets.file_description.str.contains('1-s2'),'content']:
        frame=read_sheet(blob)
        if frame is not None:frames.append(frame)
    assert len(frames)==1
    meta=frames[0]
    meta['Age']=pd.to_numeric(meta['Age'],errors='coerce')
    eligible=meta.loc[meta.Histologic_type.str.strip().eq('Serous') & meta.Case_excluded.str.strip().eq('No')]
    oldest=eligible.loc[eligible.Age.eq(eligible.Age.max())]
    print(eligible[['idx','Age','Case_excluded']].sort_values('Age',ascending=False).to_string(index=False))
    def canonical(value):
        m=re.fullmatch(r'([A-Za-z]+)[\W_]*0*(\d+)',value.strip())
        return m.group(1).upper()+str(int(m.group(2))) if m else value
    docs=pd.read_parquet('/workspace/data/domain_docs/files.parquet')
    records=[]
    pattern=r'^(?:patients )?(.+?) (?:were hyperactivated with|had proteins|expressed|showed elevated activity for) (.+?), respectively'
    for content in docs.content:
        for line in content.splitlines():
            m=re.match(pattern,line)
            if m:
                ids=m.group(1).split(', ');proteins=m.group(2).split(', ')
                assert len(ids)==len(proteins)
                records.extend((canonical(i),p) for i,p in zip(ids,proteins))
    proteins=pd.DataFrame(records,columns=['key','protein'])
    oldest=oldest.copy();oldest['key']=oldest['idx'].map(canonical)
    result=oldest.merge(proteins,on='key',how='left')
    assert result.protein.notna().all()
    answers=result.protein.unique()
    assert len(answers)==1
    print(result[['idx','Age','protein']].to_string(index=False))
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(answers[0])})+'\n')
    meta.to_csv('/workspace/work/metadata_extracted.csv',index=False)
if __name__=='__main__':main()
