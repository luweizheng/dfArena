import re,json
from datetime import datetime,date
from pathlib import Path
import polars as pl
OUT=Path('/workspace/work')
fund=pl.read_parquet('/workspace/data/funding/Funding.parquet')
docs=pl.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
def norm(s):
 return re.sub(r'[^a-z0-9]+','_',s.lower().replace('&',' ')).strip('_')
def canonical(s):
 s=re.sub(r'_(?:fema_caloes|caljpia_fema|caljpia|caloes|fema)(?:_project)?$','',s)
 s=s.replace('outdoor_warningn','outdoor_warning')
 s=re.sub(r'^202[12]_annual_street','annual_street',s)
 aliases={
 'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
 'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
 'citywide_guardrail_replacement':'guardrail_replacement_citywide',
 'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
 'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
 'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
 'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
 'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
 'outdoor_warning_signs':'outdoor_warning_sirens',
 'outdoor_warning_sirens_design':'outdoor_warning_sirens',
 'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
 'trancas_canyon_park_upper_and_lower_slopes_repair':'trancas_canyon_park_slope_stabilization_project',
 'trancas_playground_resurfacing':'trancas_canyon_park_playground',
 'trancas_canyon_park_playground_resurfacing':'trancas_canyon_park_playground',
 'malibu_bluffs_park_south_walkway':'malibu_bluffs_park_south_walkway_repairs',
 'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
 'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
 }
 return aliases.get(s,s)
known=set(fund['project_name'].to_list())-{'discussion','recommended_action'}
rows=[]; unmatched=[]
for r in docs.iter_rows(named=True):
 t=r['report_content'];rid=r['report_id']
 ds=re.search(r'Meeting date:\s*([A-Za-z]+ \d+, \d{4})',t).group(1)
 try: dt=datetime.strptime(ds,'%B %d, %Y').date()
 except ValueError: dt=datetime.strptime(ds,'%b %d, %Y').date()
 if rid=='rid_0010':dt=date(2022,1,26)
 lines=t.splitlines();typ=None;status=None;found=set()
 for i,line in enumerate(lines):
  h=re.fullmatch(r'(Capital Improvement(?: and Disaster Recovery)?|Disaster) Projects\s*\(([^)]+)\)',line.strip())
  if h:
   typ='disaster' if h[1]=='Disaster' else 'capital';status=h[2];continue
  if not typ or not line.strip():continue
  for n in range(1,4):
   name=norm(' '.join(lines[i:i+n]))
   if name in known:
    key=canonical(name)
    if key not in found:
     rows.append(dict(report_id=rid,report_date=dt,project=key,type=typ,status=status,heading=name));found.add(key)
    break
# Combined Capital Improvement and Disaster Recovery sections use the capital
# program classification, consistent with the March 2023 capital-only sections.
reports=pl.DataFrame(rows).sort('report_date')
reports.write_csv(OUT/'project_reports.csv')
fund=fund.with_columns(pl.col('project_name').map_elements(canonical,return_dtype=pl.String).alias('project'),pl.col('grant_time').str.to_date().alias('grant_date'))
matched=fund.sort('grant_date').join_asof(reports.sort('report_date'),left_on='grant_date',right_on='report_date',by='project',strategy='backward',check_sortedness=False)
matched.write_csv(OUT/'funding_classified.csv')
totals=matched.filter(pl.col('type')=='capital').group_by(pl.col('grant_date').dt.year().alias('year')).agg(pl.col('amount').sum().alias('total_usd')).sort('total_usd',descending=True)
totals.write_csv(OUT/'annual_totals.csv')
print(totals)
print('Unrecognized funding names:',set(fund['project'].to_list())-set(reports['project'].to_list()))
print('Reports per agenda:',reports.group_by('report_id').len().sort('report_id'))
winner=totals.row(0,named=True)
(OUT/'answer.json').write_text(json.dumps({'answer':f"{winner['year']}: ${winner['total_usd']:,} USD."}))
