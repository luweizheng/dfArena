import json,re
from pathlib import Path
import pandas as pd

OUT=Path('/workspace/work')
CUT=pd.Timestamp('2023-01-01')
docs=pd.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
fund=pd.read_parquet('/workspace/data/funding/Funding.parquet')
def norm(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def entity(s):
    s=norm(s)
    s=re.sub(r'_(?:fema_caloes|caljpia_fema|fema|caloes|caljpia)(?:_project)?$','',s)
    s=re.sub(r'^202[12]_annual_street_maintenance$', 'annual_street_maintenance',s)
    aliases={
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'westward_beach_road_improvements_project':'westward_beach_road_repair_project',
      'westward_beach_road_drainage_improvements_project':'westward_beach_road_repair_project',
      'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
      'trancas_playground_resurfacing':'trancas_canyon_park_playground_resurfacing',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'citywide_guardrail_replacement':'guardrail_replacement_citywide',
    }
    return aliases.get(s,s)
names=set(fund.project_name)
# Paragraphs that exactly match a funding name are project headings, not narrative mentions.
section=re.compile(r'^(Capital Improvements? Projects|Disaster Projects)\s*\((Design|Construction|Completed|Not Started)\)$',re.I)
rows=[]
unmatched=[]
for r in docs.itertuples():
    date=pd.to_datetime(re.search(r'Meeting date:\s*([^\n]+)',r.report_content).group(1))
    if r.report_id=='rid_0010': date=pd.Timestamp('2022-01-26') # Explicit correction supplied in hints.
    if date>CUT:continue
    txt=re.sub(r'Page \d+ of \d+\s*Agenda Item # [^\n]+','',r.report_content)
    kind=status=None
    lines=txt.splitlines()
    for i,line in enumerate(lines):
        block=line.strip()
        if norm(block) not in names and not section.fullmatch(block):
            for width in (2,3):
                candidate=' '.join(' '.join(lines[i:i+width]).split())
                if norm(candidate) in names:
                    block=candidate
                    break
        m=section.fullmatch(block)
        if m:
            kind='capital' if m[1].lower().startswith('capital') else 'disaster'
            status=m[2].lower()
        elif kind and norm(block) in names:
            rows.append(dict(project=entity(block),name=block,date=date,report_id=r.report_id,type=kind,status=status))
        elif kind and block and '(cid:' not in block:
            unmatched.append((r.report_id,block))
reports=pd.DataFrame(rows)
reports.to_csv(OUT/'extracted_reports.csv',index=False)
latest=reports.sort_values('date').drop_duplicates('project',keep='last')
fund['date']=pd.to_datetime(fund.grant_time)
fund['project']=fund.project_name.map(entity)
totals=fund.loc[fund.date<=CUT].groupby('project').amount.sum().rename('total_funding')
result=latest.join(totals,on='project')
result.to_csv(OUT/'latest_projects.csv',index=False)
result=result.loc[(result.type=='capital') & (result.status=='design') & (result.total_funding>500000)].sort_values('project')
# Display the ongoing annual program without a cycle year.
result['name']=result.apply(lambda r: 'Annual Street Maintenance' if r.project=='annual_street_maintenance' else r['name'],axis=1)
answer='; '.join(result['name'])+'.'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(result[['name','total_funding','report_id']].to_string(index=False))
(OUT/'unmatched_lines.json').write_text(json.dumps(unmatched,indent=2))
