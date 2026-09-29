import re,json
from pathlib import Path
import pandas as pd
ROOT=Path('/workspace/work')
def norm(s):
 return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def canonical(s):
 s=norm(s)
 s=re.sub(r'_(?:fema_caloes|caljpia_fema|caljpia|caloes|fema)_project$','',s)
 s=re.sub(r'^202[12]_annual_street','annual_street',s)
 aliases={
 'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
 'citywide_guardrail_replacement':'guardrail_replacement_citywide',
 'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
 'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
 'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
 'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
 'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
 'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
 'trancas_canyon_park_upper_and_lower_slopes_repair':'trancas_canyon_park_slope_stabilization_project',
 'trancas_playground_resurfacing':'trancas_canyon_park_playground_resurfacing',
 'trancas_canyon_park_playground':'trancas_canyon_park_playground_resurfacing',
 'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
 'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
 'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
 'westward_beach_road_drainage_improvements_project':'westward_beach_road_shoulder_repairs',
 'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
 'outdoor_warning_sirens_design':'outdoor_warning_sirens',
 'outdoor_warning_sirens_fema':'outdoor_warning_sirens',
 'outdoor_warning_signs':'outdoor_warning_sirens',
 'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
 }
 return aliases.get(s,s)
docs=pd.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
fund=pd.read_parquet('/workspace/data/funding/Funding.parquet')
names=set(fund.project_name)-{'discussion','recommended_action'}
records=[]
section=re.compile(r'(?:Capital Improvement(?: and Disaster Recovery)?|Disaster(?: Recovery)?) Projects\s*\((Design|Construction|Completed|Not Started)\)',re.I)
for r in docs.itertuples():
 date=pd.Timestamp('2022-01-26') if r.report_id=='rid_0010' else pd.to_datetime(re.search(r'Meeting date:\s*([^\n]+)',r.report_content,re.I).group(1))
 if not pd.Timestamp('2021-06-01')<=date<=pd.Timestamp('2023-01-01'):continue
 status=None
 for line in r.report_content.splitlines():
  m=section.search(line)
  if m:
   status=m.group(1).lower();continue
  key=norm(line)
  if status and key in names:
   records.append(dict(report_id=r.report_id,date=date,name=key,project=canonical(key),status=status))
obs=pd.DataFrame(records).drop_duplicates()
obs.to_csv(ROOT/'project_statuses.csv',index=False)
# Require different reports as well as different status categories.
eligible=[]
for p,g in obs.groupby('project'):
 if any(a.report_id!=b.report_id and a.status!=b.status for a in g.itertuples() for b in g.itertuples()):eligible.append(p)
fund['project']=fund.project_name.map(canonical)
fund['date']=pd.to_datetime(fund.grant_time)
f= fund[fund.date.between('2021-06-01','2023-01-01')]
totals=f.groupby('project').amount.sum().reindex(eligible,fill_value=0)
totals.to_csv(ROOT/'eligible_project_funding.csv')
answer=f'${totals.mean():,.2f} USD'
(ROOT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(obs.groupby('project').status.agg(lambda s:', '.join(sorted(set(s)))).to_string())
print(totals.to_string());print('Projects:',len(totals),'Total:',totals.sum(),'Average:',answer)
