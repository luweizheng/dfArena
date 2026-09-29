import re,json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import ibis
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pacsv

OUT=Path('/workspace/work')
c=ibis.duckdb.connect()
docs=c.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
f=c.read_parquet('/workspace/data/funding/Funding.parquet')

def norm(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')

def canonical(s):
    s=norm(s)
    s=re.sub(r'_(?:fema_caloes|caljpia_fema|fema|caloes|caljpia)(?:_project)?$','',s)
    s=re.sub(r'^202[12]_annual_street','annual_street',s)
    aliases={
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'citywide_guardrail_replacement':'guardrail_replacement_citywide',
      'trancas_playground_resurfacing':'trancas_canyon_park_playground_resurfacing',
      'trancas_canyon_park_playground':'trancas_canyon_park_playground_resurfacing',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_signs':'outdoor_warning_sirens',
      'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
      'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
      'westward_beach_road_drainage_improvements_project':'westward_beach_road_shoulder_repairs',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
      'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
      'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
    }
    return aliases.get(s,s)

names=f.select('project_name').distinct().to_pyarrow().column(0).to_pylist()
known={canonical(n) for n in names}-{ 'discussion','recommended_action' }
rows=[]
for doc in docs.to_pyarrow().to_pylist():
    txt=doc['report_content']
    date=re.search(r'Meeting date:\s*([^\n]+)',txt).group(1).strip()
    if doc['report_id']=='rid_0010':date='January 26, 2022'
    # Dates are converted and filtered in Ibis; Python only extracts text.
    lines=txt.splitlines()
    status=None
    for pos,line in enumerate(lines):
        m=re.search(r'(?:Capital Improvement|Disaster).*Projects\s*\((Design|Construction|Completed|Not Started)\)',line)
        if m:status=m.group(1).lower();continue
        if status is None:continue
        title=line.strip()
        key=canonical(title)
        if key in known:
            rows.append(dict(report_id=doc['report_id'],date_text=re.sub(r'^Jun ', 'June ',date),project=key,status=status,position=pos,title=title))

pq.write_table(pa.Table.from_pylist(rows), OUT/'extracted.parquet')
r=c.read_parquet(OUT/'extracted.parquet')
r=r.mutate(report_date=r.date_text.as_timestamp('%B %d, %Y').date())
# Only reports on or before the funding window's end can affect this task.
r=r.filter(r.report_date<=ibis.date('2022-09-01'))
# Repeated project headings in a report use the final explicit status section.
r=r.mutate(rn=ibis.row_number().over(ibis.window(group_by=['report_id','project'],order_by=ibis.desc('position')))).filter(lambda t:t.rn==0).drop('rn')
pacsv.write_csv(r.order_by('report_date','position').to_pyarrow(), OUT/'extracted_statuses.csv')
pq.write_table(pa.Table.from_pylist([{'project_name':n,'project':canonical(n)} for n in names if canonical(n) in known]),OUT/'aliases.parquet')
maptable=c.read_parquet(OUT/'aliases.parquet')
f=f.mutate(grant_date=f.grant_time.cast('date'))
f=f.filter(f.grant_date.between(ibis.date('2021-09-01'),ibis.date('2022-09-01')))
f=f.join(maptable,'project_name').select(f, maptable.project)
j=f.join(r,[f.project==r.project,f.grant_date>=r.report_date]).select(f, r.report_date,r.report_id,r.status)
j=j.mutate(rn=ibis.row_number().over(ibis.window(group_by='fid',order_by=ibis.desc('report_date')))).filter(lambda t:t.rn==0).drop('rn')
pacsv.write_csv(j.order_by('grant_date','fid').to_pyarrow(), OUT/'funding_status_audit.csv')
totals=j.group_by('status').aggregate(total=j.amount.sum()).to_pyarrow().to_pylist()
d={x['status']:x['total'] for x in totals}
answer=(Decimal(d['completed'])/Decimal(d['not started'])).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
(OUT/'answer.json').write_text(json.dumps({'answer':str(answer)}))
print(totals)
print(answer)
