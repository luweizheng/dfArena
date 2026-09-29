import re,json
from datetime import datetime,date
from pathlib import Path
import polars as pl
OUT=Path('/workspace/work')
END=date(2022,6,1)
START=date(2021,6,1)

def key(s):
    s=re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
    s=re.sub(r'_(?:caljpia_fema|fema_caloes|fema|caloes|caljpia)(?:_project)?$','',s)
    s=re.sub(r'^202[12]_annual_street','annual_street',s)
    aliases={
      'guardrail_replacement_citywide':'citywide_guardrail_replacement',
      'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_signs':'outdoor_warning_sirens',
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'trancas_canyon_park_playground':'trancas_playground_resurfacing',
      'trancas_canyon_park_playground_resurfacing':'trancas_playground_resurfacing',
      'trancas_canyon_park_upper_and_lower_slopes_repair':'trancas_canyon_park_slope_stabilization_project',
      'westward_beach_road_repair_project':'westward_beach_road_shoulder_repairs',
      'westward_beach_road_drainage_improvements_project':'westward_beach_road_improvements_project',
      'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch':'pch_overhead_warning_signs',
      'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
      'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
    }
    return aliases.get(s,s)

fund=pl.read_parquet('/workspace/data/funding/Funding.parquet').with_columns(
 pl.col('project_name').map_elements(key,return_dtype=pl.String).alias('project'),
 pl.col('grant_time').str.to_date().alias('grant_date'))
known=set(fund['project'])-{'discussion','recommended_action'}
rows=[]
for r in pl.read_parquet('/workspace/data/civic_docs/civic_docs.parquet').iter_rows(named=True):
    t=r['report_content']
    ds=re.search(r'Meeting date:\s*([^\n]+)',t).group(1)
    try: day=datetime.strptime(ds,'%B %d, %Y').date()
    except ValueError: day=datetime.strptime(ds,'%b %d, %Y').date()
    if r['report_id']=='rid_0010':day=date(2022,1,26)
    if day>END:continue
    typ=None
    for raw in t.splitlines():
        line=raw.strip()
        if re.match(r'Capital Improvement Projects\s*\(',line):typ='capital';continue
        if re.match(r'Disaster Projects\s*\(',line):typ='disaster';continue
        # Some titles share their line with the first bullet or description.
        title=re.split(r'\(cid:|Project Description:',line)[0].strip()
        k=key(title)
        if typ and k in known:
            rows.append({'project':k,'report_date':day,'type':typ,'report_id':r['report_id'],'title':title})
reports=pl.DataFrame(rows).unique()
assert reports.group_by('project','report_date').agg(pl.col('type').n_unique()).filter(pl.col('type')>1).is_empty()
reports=reports.unique(subset=['project','report_date']).sort('report_date')
reports.write_csv(OUT/'project_reports.csv')
period=fund.filter(pl.col('grant_date').is_between(START,END))
matched=period.sort('grant_date').join_asof(reports,by='project',left_on='grant_date',right_on='report_date',strategy='backward',check_sortedness=False)
matched.write_csv(OUT/'funding_classified.csv')
print('UNMATCHED')
print(matched.filter(pl.col('type').is_null()).group_by('project').agg(pl.len(),pl.col('amount').sum()).sort('project'))
print('TYPE CHANGES')
print(reports.group_by('project').agg(pl.col('type').n_unique()).filter(pl.col('type')>1))
totals=matched.filter(pl.col('type').is_not_null()).group_by('type').agg(pl.col('amount').sum())
print(totals)
t=dict(totals.iter_rows())
ratio=t['capital']/t['disaster']
(OUT/'answer.json').write_text(json.dumps({'answer':f'{ratio:.2f}'})+'\n')
print('ANSWER',f'{ratio:.2f}')
