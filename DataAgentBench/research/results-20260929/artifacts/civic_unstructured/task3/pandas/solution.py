import pandas as pd
import re,json
from pathlib import Path
OUT=Path('/workspace/work')
CUTOFF=pd.Timestamp('2022-08-01')
def norm(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
# Entity aliases established from agenda titles and descriptions, independent of status.
def canonical(s):
    s=norm(s)
    s=re.sub(r'_(?:fema_caloes|caljpia_fema|fema|caloes|caljpia)(?:_project)?$','',s)
    s=re.sub(r'^20\d\d_(?=annual_street_maintenance)','',s)
    aliases={
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'guardrail_replacement_citywide':'citywide_guardrail_replacement',
      'malibu_park_drainage_improvements':'malibu_park_storm_drain_repairs',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_signs':'outdoor_warning_sirens',
      'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
      'trancas_playground_resurfacing':'trancas_canyon_park_playground_resurfacing',
      'trancas_canyon_park_playground':'trancas_canyon_park_playground_resurfacing',
      'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
      'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
    }
    return aliases.get(s,s)
fund=pd.read_parquet('/workspace/data/funding/Funding.parquet')
docs=pd.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
noise={'discussion','recommended_action'}
known={canonical(n) for n in fund.project_name if n not in noise}
rows=[]
for r in docs.itertuples():
    date=pd.to_datetime(re.search(r'Meeting date:\s*([^\n]+)',r.report_content).group(1))
    if r.report_id=='rid_0010':date=pd.Timestamp('2022-01-26')
    if date>CUTOFF:continue
    lines=r.report_content.splitlines()
    status=None
    for i,line in enumerate(lines):
        m=re.search(r'Projects\s*\((Design|Construction|Completed|Not Started)\)',line,re.I)
        if m:status=m.group(1).lower();continue
        if not status or not line.strip():continue
        for k in (1,2,3):
            title=' '.join(lines[i:i+k]).strip()
            key=canonical(title)
            if key in known:
                rows.append(dict(report_id=r.report_id,date=date,project=key,status=status,title=title))
                break
reports=pd.DataFrame(rows).drop_duplicates(['report_id','project','status'])
reports.to_csv(OUT/'extracted_reports.csv',index=False)
latest=reports.sort_values('date').drop_duplicates('project',keep='last')
latest.to_csv(OUT/'latest_status.csv',index=False)
fund['date']=pd.to_datetime(fund.grant_time)
fund['project']=fund.project_name.map(canonical)
fund=fund[(fund.date<=CUTOFF)&~fund.project_name.isin(noise)]
fund=fund.drop_duplicates(['funding_source','project'])
joined=fund.merge(latest[['project','status']],on='project',how='left')
assert joined.status.notna().all(), 'An eligible funded project lacks a report match'
joined['completed']=joined.status.eq('completed')
joined.to_csv(OUT/'funded_projects.csv',index=False)
summary=joined.groupby('funding_source').agg(projects=('project','nunique'),completed=('completed','sum'))
summary['share']=summary.completed/summary.projects
summary.to_csv(OUT/'source_summary.csv')
print(latest[['project','status','report_id']].sort_values('project').to_string(index=False))
print('UNMATCHED',joined.loc[joined.status.isna(),'project'].unique())
print(summary)
qualified=summary.index[summary.completed*4>=summary.projects].tolist()
answer='; '.join(qualified) if qualified else 'No funding sources meet the 25% threshold.'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
