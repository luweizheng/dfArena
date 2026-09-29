import json,re
from datetime import datetime,date
from pathlib import Path
import polars as pl
OUT=Path('/workspace/work')
CUTOFF=date(2022,8,1)
def normalize(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
# Semantic aliases established from agenda headings and project descriptions.
GROUPS=[
 ['annual_street_maintenance','2021_annual_street_maintenance','2022_annual_street_maintenance','2022_morning_view_resurfacing_storm_drain_improvements'],
 ['storm_drain_trash_screens','storm_drain_trash_screens_phase_two'],
 ['citywide_guardrail_replacement','guardrail_replacement_citywide'],
 ['broad_beach_road_water_quality_infrastructure_repairs','broad_beach_road_water_quality_repair'],
 ['clover_heights_storm_drain','clover_heights_storm_drainage_improvements'],
 ['encinal_canyon_road_drainage_improvements','encinal_canyon_road_repairs'],
 ['latigo_canyon_road_roadway_retaining_wall_improvements','latigo_canyon_road_retaining_wall_repair_project'],
 ['malibu_bluffs_park_south_walkway','malibu_bluffs_park_south_walkway_repairs'],
 ['malibu_park_drainage_improvements','malibu_park_storm_drain_repairs'],
 ['outdoor_warning_sirens','outdoor_warning_sirens_design','outdoor_warningn_sirens_design','outdoor_warning_signs'],
 ['point_dume_decomposed_granite_walkway_repair_project','point_dume_walkway_repairs'],
 ['trancas_playground_resurfacing','trancas_canyon_park_playground_resurfacing','trancas_canyon_park_playground'],
 ['trancas_canyon_park_slope_stabilization_project','trancas_canyon_park_upper_and_lower_slopes_repair'],
 ['westward_beach_road_improvements_project','westward_beach_road_repair_project'],
 ['westward_beach_road_shoulder_repairs','westward_beach_road_drainage_improvements_project'],
 ['michael_landon_center_roof_replacement_project','malibu_bluffs_park_roof_replacement_project'],
 ['pch_overhead_warning_signs','pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch'],
]
ALIASES={v:g[0] for g in GROUPS for v in g}
def canonical(s):
    s=normalize(s)
    s=re.sub(r'_(?:(?:fema|caloes|caljpia)_?)+(?:project)?$','',s)
    return ALIASES.get(s,s)
fund=pl.read_parquet('/workspace/data/funding/Funding.parquet')
names=set(fund['project_name'])-{'discussion','recommended_action'}
docs=pl.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
rows=[]; dates=[]
for r in docs.iter_rows(named=True):
    t=r['report_content']
    ds=re.search(r'Meeting date:\s*([^\n]+)',t,re.I).group(1)
    try: dt=datetime.strptime(ds,'%B %d, %Y').date()
    except ValueError: dt=datetime.strptime(ds,'%b %d, %Y').date()
    if r['report_id']=='rid_0010':dt=date(2022,1,26)
    dates.append({'report_id':r['report_id'],'date':dt})
    status=None
    for i,line in enumerate(t.splitlines()):
        line=line.strip()
        m=re.search(r'Projects\s*\((Design|Construction|Completed|Not Started)\)',line,re.I)
        if m:status=m.group(1).lower()
        if status and normalize(line) in names:
            rows.append({'report_id':r['report_id'],'date':dt,'line':i,'heading':line,'project':canonical(line),'status':status})
reports=pl.DataFrame(rows)
reports.write_csv(OUT/'extracted_statuses.csv')
pl.DataFrame(dates).write_csv(OUT/'report_dates.csv')
latest=(reports.filter(pl.col('date')<=CUTOFF).sort(['date','line']).unique('project',keep='last').select('project','status','date','report_id'))
latest.write_csv(OUT/'latest_statuses.csv')
valid=set(reports['project'])
fund=fund.with_columns(pl.col('project_name').map_elements(canonical,return_dtype=pl.String).alias('project'),pl.col('grant_time').str.to_date())
fund.filter(~pl.col('project').is_in(valid)).write_csv(OUT/'excluded_funding.csv')
projects=(fund.filter((pl.col('grant_time')<=CUTOFF)&pl.col('project').is_in(valid)).select('funding_source','project').unique().join(latest,on='project',how='left').with_columns((pl.col('status')=='completed').fill_null(False).alias('completed')))
projects.write_csv(OUT/'funded_project_statuses.csv')
summary=projects.group_by('funding_source').agg(pl.len().alias('projects'),pl.col('completed').sum().alias('completed')).with_columns((pl.col('completed')/pl.col('projects')*100).alias('percent')).sort('funding_source')
summary.write_csv(OUT/'source_summary.csv')
winners=summary.filter(pl.col('completed')*4>=pl.col('projects'))['funding_source'].to_list()
answer='; '.join(winners) if winners else 'No funding sources meet the 25% completed-project threshold as of 2022-08-01.'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(summary)
print('Completed:',latest.filter(pl.col('status')=='completed').to_dicts())
print('Answer:',answer)
