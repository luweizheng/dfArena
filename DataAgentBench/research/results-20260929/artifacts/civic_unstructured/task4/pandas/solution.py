import re,json
from pathlib import Path
import pandas as pd
BASE=Path('/workspace/data'); OUT=Path('/workspace/work')

def norm(s):
    s=re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
    s=re.sub(r'_(?:(?:fema|caloes|caljpia)_?)+(?:project)?$','',s).rstrip('_')
    s=re.sub(r'^20\d\d_annual_street','annual_street',s)
    s=s.replace('warningn','warning')
    aliases={
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'trancas_canyon_park_playground_resurfacing':'trancas_playground_resurfacing',
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'citywide_guardrail_replacement':'guardrail_replacement_citywide',
      'westward_beach_road_repair_project':'westward_beach_road_shoulder_repairs',
      'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch':'pch_overhead_warning_signs',
    }
    return aliases.get(s,s)

docs=pd.read_parquet(BASE/'civic_docs/civic_docs.parquet')
fund=pd.read_parquet(BASE/'funding/Funding.parquet')
fund['project']=fund.project_name.map(norm)
known=set(fund.project)
rows=[]
section=re.compile(r'^(Capital Improvement Projects|Disaster Projects)\s*\((Design|Construction|Completed|Not Started)\)',re.I)
for r in docs.itertuples():
    date=pd.to_datetime(re.search(r'Meeting date:\s*([^\n]+)',r.report_content,re.I).group(1))
    if r.report_id=='rid_0010':date=pd.Timestamp('2022-01-26')
    if date>pd.Timestamp('2022-06-01'):continue
    typ=None; status=None
    for line in r.report_content.splitlines():
        line=line.strip()
        m=section.match(line)
        if m:
            typ='capital' if m[1].lower().startswith('capital') else 'disaster'
            status=m[2].lower();line=line[m.end():].strip()
        # Some project titles immediately precede a bullet on the same line.
        line=line.split('(cid:')[0].strip()
        key=norm(line)
        if typ and key in known:
            rows.append({'project':key,'report_date':date,'type':typ,'status':status,'report_id':r.report_id,'title':line})
history=pd.DataFrame(rows).drop_duplicates()
history.to_csv(OUT/'project_history.csv',index=False)
fund['grant_date']=pd.to_datetime(fund.grant_time)
f=fund[fund.grant_date.between('2021-06-01','2022-06-01')].copy()
# Backward as-of matching is per project, preserving every funding record.
joined=pd.merge_asof(f.sort_values('grant_date'),history.sort_values('report_date'),left_on='grant_date',right_on='report_date',by='project',direction='backward')
joined.to_csv(OUT/'funding_audit.csv',index=False)
totals=joined.groupby('type').amount.sum()
print(totals.to_string())
print('Unmatched:');print(joined[joined.type.isna()].groupby('project_name').amount.agg(['count','sum']).to_string())
answer=f"{totals['capital']/totals['disaster']:.2f}"
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(answer)
