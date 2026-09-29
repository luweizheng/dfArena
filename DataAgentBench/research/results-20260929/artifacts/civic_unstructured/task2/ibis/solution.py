import json,re
from pathlib import Path
import ibis
import pyarrow as pa

OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
docs=con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
funding=con.read_parquet('/workspace/data/funding/Funding.parquet')
names=funding.select('project_name').distinct().to_pyarrow().column('project_name').to_pylist()

def normalize(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')

def canonical(s):
    s=re.sub(r'_(?:caljpia_fema|fema_caloes|fema|caloes|caljpia)_project$','',s)
    s=re.sub(r'^202[12]_annual_street_maintenance$', 'annual_street_maintenance',s)
    aliases={
      'guardrail_replacement_citywide':'citywide_guardrail_replacement',
      'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
      'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
      'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
      'westward_beach_road_drainage_improvements_project':'westward_beach_road_shoulder_repairs',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'trancas_playground_resurfacing':'trancas_canyon_park_playground',
      'trancas_canyon_park_playground_resurfacing':'trancas_canyon_park_playground',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_fema':'outdoor_warning_sirens',
      'outdoor_warning_signs':'outdoor_warning_sirens',
    }
    return aliases.get(s,s)

# Python handles only text extraction and semantic alias resolution; all
# filtering, date parsing, latest-report selection, joins and sums use Ibis.
rows=[]
for doc in docs.to_pyarrow().to_pylist():
    text=doc['report_content']
    date=re.search(r'Meeting date:\s*([^\n]+)',text,re.I).group(1).strip()
    if doc['report_id']=='rid_0010': date='January 26, 2022'
    status=None
    for line in text.splitlines():
        heading=re.search(r'Projects\s*\((Design|Construction|Completed|Not Started)\)',line,re.I)
        if heading:
            status=heading.group(1).lower()
            continue
        name=normalize(line.strip())
        if status and name in names and name not in {'discussion','recommended_action'}:
            rows.append(dict(project=canonical(name),raw_name=name,status=status,report_id=doc['report_id'],meeting_date=date))
print('EXTRACTED',len(rows),'NAMES',names[:3])
status_table=con.create_table('extracted_statuses',obj=ibis.memtable(pa.Table.from_pylist(rows)))
status_table=status_table.mutate(report_date=status_table.meeting_date.re_replace(r'^Jun ', 'June ').as_timestamp('%B %d, %Y').date())
cutoff=ibis.date('2023-01-01')
before=status_table.filter(status_table.report_date<=cutoff)
latest_dates=before.group_by('project').aggregate(latest_date=before.report_date.max())
latest=before.join(latest_dates,(before.project==latest_dates.project)&(before.report_date==latest_dates.latest_date)).select(before)
completed=latest.filter(latest.status=='completed').select('project').distinct()
mapping=con.create_table('project_aliases',obj=ibis.memtable(pa.Table.from_pylist([dict(project_name=n,project=canonical(n)) for n in names if n not in {'discussion','recommended_action'}])))
f=funding.mutate(grant_date=funding.grant_time.cast('date'))
f=f.filter(f.grant_date<=cutoff).join(mapping,'project_name')
totals=f.group_by('project').aggregate(total_usd=f.amount.sum())
ranked=totals.join(completed,'project').select(totals).order_by(ibis.desc('total_usd'),'project')
result=ranked.to_pyarrow().to_pylist()
assert result
OUT.joinpath('ranking.json').write_text(json.dumps(result,indent=2))
OUT.joinpath('latest_statuses.json').write_text(json.dumps(latest.to_pyarrow().to_pylist(),indent=2,default=str))
winner=result[0]
display=winner['project'].replace('_',' ').title()
answer=f"{display} — ${winner['total_usd']:,} USD."
OUT.joinpath('answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(json.dumps(result,indent=2))
print(answer)
