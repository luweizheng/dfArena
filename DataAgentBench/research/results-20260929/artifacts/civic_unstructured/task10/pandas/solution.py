import pandas as pd
import re,json
from pathlib import Path
OUT=Path('/workspace/work')
def norm(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def entity(s):
    s=norm(s)
    s=re.sub(r'_(?:caljpia_fema|fema_caloes|caljpia|caloes|fema)_project$','',s)
    s=re.sub(r'^202[12]_annual','annual',s)
    aliases={
      'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'citywide_guardrail_replacement':'guardrail_replacement_citywide',
      'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'trancas_playground_resurfacing':'trancas_canyon_park_playground',
      'trancas_canyon_park_playground_resurfacing':'trancas_canyon_park_playground',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_fema':'outdoor_warning_sirens',
      'outdoor_warning_signs':'outdoor_warning_sirens',
      'point_dume_decomposed_granite_walkway_repair_project':'point_dume_walkway_repairs',
      'trancas_canyon_park_upper_and_lower_slopes_repair':'trancas_canyon_park_slope_stabilization_project',
      'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
      'westward_beach_road_drainage_improvements_project':'westward_beach_road_shoulder_repairs',
      'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
    }
    return aliases.get(s,s)
fund=pd.read_parquet('/workspace/data/funding/Funding.parquet')
docs=pd.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
known=set(fund.project_name.map(entity))-{'discussion','recommended_action'}
rows=[]
for r in docs.itertuples():
    date=pd.Timestamp(re.search(r'Meeting date:\s*([^\n]+)',r.report_content,re.I).group(1))
    if r.report_id=='rid_0010':date=pd.Timestamp('2022-01-26')
    if date>pd.Timestamp('2022-09-01'):continue
    status=None
    for line in r.report_content.splitlines():
        line=line.strip()
        m=re.search(r'^(?:Capital Improvement(?: and Disaster Recovery)?|Disaster(?: Recovery)?) Projects?\s*\((Design|Construction|Completed|Not Started)\)',line,re.I)
        if m:
            status=m.group(1).lower();continue
        key=entity(line)
        if status and key in known:
            rows.append(dict(project=key,report_date=date,status=status,report_id=r.report_id,heading=line))
history=pd.DataFrame(rows)
# A few agendas repeat an old title in Design and the renamed project in
# Completed; the final, explicit completed entry supplies the current status.
history=history.drop_duplicates(['project','report_date'],keep='last')
history.to_csv(OUT/'status_history.csv',index=False)
fund['project']=fund.project_name.map(entity)
fund['grant_date']=pd.to_datetime(fund.grant_time)
fund=fund[fund.grant_date.between('2021-09-01','2022-09-01')].copy()
matched=pd.merge_asof(fund.sort_values('grant_date'),history.sort_values('report_date'),left_on='grant_date',right_on='report_date',by='project',direction='backward')
matched.to_csv(OUT/'classified_funding.csv',index=False)
totals=matched.groupby('status').amount.sum()
ratio=totals['completed']/totals['not started']
(OUT/'answer.json').write_text(json.dumps({'answer':f'{ratio:.2f}'}))
print(totals.to_string());print('Ratio:',f'{ratio:.2f}')
print('No status:',matched.loc[matched.status.isna(),'project_name'].value_counts().to_string())
print(history.groupby('report_id').size().to_string())
