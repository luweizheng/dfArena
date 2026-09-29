import json,re
from datetime import datetime,date
from pathlib import Path
import polars as pl

ROOT=Path('/workspace/data'); OUT=Path('/workspace/work'); cutoff=date(2022,11,1)
def slug(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def canonical(s):
    s=slug(s)
    s=re.sub(r'_(?:caljpia_fema|fema_caloes|caljpia|caloes|fema)(?:_project)?$','',s)
    s=re.sub(r'^202[12]_annual_street_maintenance$','annual_street_maintenance',s)
    aliases={
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      # Both descriptions identify warning beacons near Moonshadows and Big Rock.
      'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
      'citywide_guardrail_replacement':'guardrail_replacement_citywide',
      'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'trancas_playground_resurfacing':'trancas_canyon_park_playground',
      'trancas_canyon_park_playground_resurfacing':'trancas_canyon_park_playground',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_signs':'outdoor_warning_sirens',
      'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
      'westward_beach_road_drainage_improvements_project':'westward_beach_road_shoulder_repairs',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
      'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
      'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
      'trancas_canyon_park_upper_and_lower_slopes_repair':'trancas_canyon_park_slope_stabilization_project',
      '2022_morning_view_resurfacing_storm_drain_improvements':'annual_street_maintenance',
    }
    return aliases.get(s,s)
fund=pl.read_parquet(ROOT/'funding/Funding.parquet').with_columns(pl.col('project_name').map_elements(canonical,return_dtype=pl.String).alias('project'),pl.col('grant_time').str.to_date())
known=set(fund['project'])-{'discussion','recommended_action'}
rows=[]; dates=[]
for r in pl.read_parquet(ROOT/'civic_docs/civic_docs.parquet').iter_rows(named=True):
    t=r['report_content']
    ds=re.search(r'Meeting date:\s*([^\n]+)',t)[1].strip()
    try: dt=datetime.strptime(ds,'%B %d, %Y').date()
    except ValueError: dt=datetime.strptime(ds,'%b %d, %Y').date()
    if r['report_id']=='rid_0010':dt=date(2022,1,26)
    dates.append({'report_id':r['report_id'],'date':dt.isoformat(),'stated_date':ds})
    typ=None; status=None
    # Join wrapped agency suffixes; project heading names themselves fit on a line.
    t=re.sub(r'\(FEMA/CalOES\s*\n\s*Project\)', '(FEMA/CalOES Project)',t)
    for line in t.splitlines():
        line=line.strip()
        m=re.match(r'(Capital Improvement|Disaster) Projects\s*\((Design|Construction|Completed|Not Started)\)',line,re.I)
        if m:
            typ='disaster' if m[1].lower()=='disaster' else 'capital';status=m[2].lower();continue
        p=canonical(line)
        if typ and p in known:
            rows.append({'project':p,'date':dt,'report_id':r['report_id'],'type':typ,'status':status,'heading':line})
reports=pl.DataFrame(rows)
reports.write_csv(OUT/'extracted_projects.csv')
latest=reports.filter(pl.col('date')<=cutoff).sort('date').unique('project',keep='last')
funded=fund.filter((pl.col('grant_time')<=cutoff)&~pl.col('project').is_in(['discussion','recommended_action'])).select('funding_source','project').unique()
joined=funded.join(latest.select('project','type','date','report_id'),on='project',how='left')
joined.write_csv(OUT/'funded_projects_asof.csv')
summary=joined.group_by('funding_source').agg(pl.len().alias('projects'),(pl.col('type')=='disaster').fill_null(False).sum().alias('disaster_projects')).with_columns((pl.col('disaster_projects')/pl.col('projects')).alias('share')).sort('funding_source')
summary.write_csv(OUT/'source_shares.csv')
selected=summary.filter(pl.col('disaster_projects')*100>pl.col('projects')*55)
answer='; '.join(f"{r['funding_source']} ({r['disaster_projects']}/{r['projects']}, {r['share']:.2%})" for r in selected.iter_rows(named=True))
if selected.is_empty():
    answer='No funding sources meet the more-than-55% threshold as of 2022-11-01.'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(summary)
print('Unmatched funded projects:',joined.filter(pl.col('type').is_null())['project'].unique().sort().to_list())
print('Answer:',answer)
(OUT/'report_dates.json').write_text(json.dumps(dates,indent=2))
