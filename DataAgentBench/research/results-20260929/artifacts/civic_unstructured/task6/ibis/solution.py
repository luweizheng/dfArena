"""Extract agenda facts, resolve aliases, and compute as-of funding using Ibis/DuckDB."""
import json,re
from pathlib import Path
import ibis
import pyarrow as pa
OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
docs=con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
fund=con.read_parquet('/workspace/data/funding/Funding.parquet')
def norm(s):
 return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def canonical(s):
 s=norm(s)
 s=re.sub(r'_(?:caljpia_fema|fema_caloes|fema|caloes|caljpia)(?:_project)?$','',s)
 s=re.sub(r'^20\d\d_(?=annual_street_maintenance)','',s)
 aliases={
 'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
 'citywide_guardrail_replacement':'guardrail_replacement_citywide',
 'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
 'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
 'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
 'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
 'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
 'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
 'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
 'outdoor_warning_signs':'outdoor_warning_sirens',
 'outdoor_warning_sirens_design':'outdoor_warning_sirens',
 'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
 'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
 'trancas_playground_resurfacing':'trancas_canyon_park_playground',
 'trancas_canyon_park_playground_resurfacing':'trancas_canyon_park_playground',
 'trancas_canyon_park_upper_and_lower_slopes_repair':'trancas_canyon_park_slope_stabilization_project',
 'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
 }
 return aliases.get(s,s)
names=fund.select('project_name').distinct().to_pyarrow().to_pylist()
lookup={norm(r['project_name']) for r in names} - {'discussion','recommended_action'}
rows=[]
for doc in docs.to_pyarrow().to_pylist():
 text=doc['report_content']
 date=re.search(r'Meeting date:\s*([^\n]+)',text).group(1).strip().replace('Jun ', 'June ')
 if doc['report_id']=='rid_0010':date='January 26, 2022'
 lines=[l.strip() for l in text.splitlines() if l.strip()]
 category=None
 for i,line in enumerate(lines):
  if re.match(r'^(Capital Improvement(?: and Disaster Recovery)?|Disaster) Projects \(',line):
   # Combined headings continue the capital grouping introduced March 2023.
   category='capital' if line.startswith('Capital') else 'disaster'
  if category is None:continue
  for n in range(1,4):
   title=' '.join(lines[i:i+n]); key=norm(title)
   if key in lookup:
    rows.append(dict(project=canonical(key),report_id=doc['report_id'],report_date_text=date,project_type=category,title=title))
    break
(OUT/'extracted_reports.json').write_text(json.dumps(rows,indent=2))
reports=ibis.memtable(pa.Table.from_pylist(rows))
reports=reports.mutate(report_date=reports.report_date_text.as_timestamp('%B %d, %Y').date()).select('project','report_id','report_date','project_type').distinct()
conflicts=reports.group_by('project','report_id').aggregate(n=ibis._.count()).filter(ibis._.n>1).to_pyarrow().to_pylist()
assert not conflicts,conflicts
aliases=ibis.memtable(pa.Table.from_pylist([dict(project_name=r['project_name'],project=canonical(r['project_name'])) for r in names if r['project_name'] not in {'discussion','recommended_action'}]))
f=fund.mutate(grant_date=fund.grant_time.cast('date')).join(aliases,'project_name').select(fund.fid, fund.project_name, fund.amount, 'grant_date',aliases.project)
joined=f.join(reports,[f.project==reports.project,f.grant_date>=reports.report_date]).select(f.fid,f.project_name,f.amount,f.grant_date,reports.report_date,reports.project_type,reports.report_id)
latest=joined.mutate(rn=ibis.row_number().over(ibis.window(group_by='fid',order_by=ibis.desc('report_date')))).filter(ibis._.rn==0)
annual=latest.filter(ibis._.project_type=='capital').mutate(year=ibis._.grant_date.year()).group_by('year').aggregate(total_usd=ibis._.amount.sum()).order_by(ibis.desc('total_usd'))
result=annual.to_pyarrow().to_pylist()
(OUT/'annual_totals.json').write_text(json.dumps(result,indent=2))
latest.to_parquet(str(OUT/'classified_funding.parquet'))
print(result)
print('extracted',len(rows),'classified',latest.count().execute())
print('unmatched names',aliases.anti_join(reports,'project').to_pyarrow().to_pylist())
assert result
best=result[0]
(OUT/'answer.json').write_text(json.dumps({'answer':f"{best['year']}: ${best['total_usd']:,} USD."}))
