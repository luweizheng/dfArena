import json,re
from pathlib import Path
import pandas as pd

OUT=Path('/workspace/work')
CUTOFF=pd.Timestamp('2022-11-01')
def normalize(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')

def canonical(s):
    s=normalize(s)
    s=re.sub(r'_(?:fema_caloes|caljpia_fema|caljpia|caloes|fema)(?:_project)?$','',s)
    s=re.sub(r'^20\d\d_annual_street_maintenance$','annual_street_maintenance',s)
    aliases={
      # Both descriptions locate the overhead warning beacons at Big Rock and Moonshadows.
      'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
      'outdoor_warning_signs':'outdoor_warning_sirens',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'guardrail_replacement_citywide':'citywide_guardrail_replacement',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
      'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
      'trancas_playground_resurfacing':'trancas_canyon_park_playground_resurfacing',
      'trancas_canyon_park_playground':'trancas_canyon_park_playground_resurfacing',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
    }
    return aliases.get(s,s)

fund=pd.read_parquet('/workspace/data/funding/Funding.parquet')
docs=pd.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
fund['date']=pd.to_datetime(fund.grant_time)
fund['project']=fund.project_name.map(canonical)
noise={'discussion','recommended_action'}
known=set(fund.project)-noise
rows=[]
for r in docs.itertuples():
    date=pd.Timestamp(re.search(r'Meeting date:\s*([^\n]+)',r.report_content).group(1))
    if r.report_id=='rid_0010': date=pd.Timestamp('2022-01-26')
    if date>CUTOFF:continue
    kind=status=None
    lines=r.report_content.splitlines()
    for i,line in enumerate(lines):
        m=re.fullmatch(r'\s*(Capital Improvement|Disaster) Projects \(([^)]+)\)\s*',line)
        if m:
            kind='capital' if m[1]=='Capital Improvement' else 'disaster'
            status=m[2].lower()
            continue
        if kind is None:continue
        name=canonical(line)
        if name in known:
            rows.append(dict(project=name,date=date,type=kind,status=status,report_id=r.report_id,heading=line.strip()))
reports=pd.DataFrame(rows).drop_duplicates(['project','date','type','status'])
reports.to_csv(OUT/'extracted_reports.csv',index=False)
latest=reports.sort_values('date').drop_duplicates('project',keep='last')
eligible=fund[(fund.date<=CUTOFF)&~fund.project.isin(noise)].drop_duplicates(['funding_source','project'])
missing=eligible.loc[~eligible.project.isin(latest.project),'project'].unique()
print('Unmatched funded projects:',missing)
assert len(missing)==0,missing
joined=eligible.merge(latest[['project','type','date','report_id']],on='project',how='left',suffixes=('_grant','_report'))
joined['disaster']=joined.type.eq('disaster')
summary=joined.groupby('funding_source').agg(projects=('project','nunique'),disaster_projects=('disaster','sum'))
summary['percentage']=100*summary.disaster_projects/summary.projects
summary.to_csv(OUT/'funding_source_summary.csv')
joined.to_csv(OUT/'funded_projects_audit.csv',index=False)
print(latest[['project','type','report_id']].sort_values('project').to_string(index=False))
print(summary.to_string())
selected=summary[summary.disaster_projects*100>summary.projects*55].index.tolist()
(OUT/'answer.json').write_text(json.dumps({'answer':'; '.join(selected) if selected else 'None.'},ensure_ascii=False)+'\n')
