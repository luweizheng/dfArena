import json,re
from pathlib import Path
import ibis
import pyarrow as pa

OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
fund=con.read_parquet('/workspace/data/funding/Funding.parquet')
docs=con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')

def norm(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')

def canonical(s):
    s=norm(s)
    s=re.sub(r'_(?:caljpia_fema|fema_caloes|fema|caloes|caljpia)(?:_project)?$','',s)
    s=re.sub(r'^202[12]_annual_street_maintenance$','annual_street_maintenance',s)
    aliases={
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
      'guardrail_replacement_citywide':'citywide_guardrail_replacement',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
      'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_signs':'outdoor_warning_sirens',
      'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
      'trancas_canyon_park_playground':'trancas_playground_resurfacing',
      'trancas_canyon_park_playground_resurfacing':'trancas_playground_resurfacing',
      'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
      'westward_beach_road_drainage_improvements_project':'westward_beach_road_shoulder_repairs',
    }
    return aliases.get(s,s)

names=fund.select('project_name').distinct().to_pyarrow().to_pylist()
mapping=[dict(project_name=r['project_name'],project=canonical(r['project_name'])) for r in names if r['project_name'] not in ['discussion','recommended_action']]
known={r['project'] for r in mapping}
rows=[]
for doc in docs.to_pyarrow().to_pylist():
    text=doc['report_content']
    date=re.search(r'Meeting date:\s*([^\n]+)',text).group(1).strip()
    if doc['report_id']=='rid_0010': date='January 26, 2022'
    # Text extraction only: relational date parsing and latest-report selection happen below.
    typ=None
    for line in text.splitlines():
        line=line.strip()
        sec=re.fullmatch(r'(Capital Improvement|Disaster) Projects \(([^)]+)\)',line)
        if sec:
            typ='capital' if sec[1]=='Capital Improvement' else 'disaster'
            continue
        if line.startswith('Capital Improvement and Disaster Recovery Projects ('):
            typ=None
        key=canonical(line)
        if typ and key in known:
            rows.append(dict(project=key,report_id=doc['report_id'],date_text=date.replace('Jun ', 'June '),type=typ,heading=line))
print('extracted',len(rows)); obs=ibis.memtable(pa.Table.from_pylist(rows))
obs=obs.mutate(report_date=obs.date_text.as_timestamp('%B %d, %Y').date())
cutoff=ibis.date('2022-11-01')
obs=obs.filter(obs.report_date<=cutoff)
latest=obs.mutate(rn=ibis.row_number().over(ibis.window(group_by='project',order_by=ibis.desc('report_date')))).filter(lambda t:t.rn==0)
mp=ibis.memtable(pa.Table.from_pylist(mapping))
fund=fund.mutate(grant_date=fund.grant_time.cast('date')).filter(lambda t:t.grant_date<=cutoff)
pairs=fund.join(mp,'project_name').select('funding_source','project').distinct()
joined=pairs.left_join(latest,'project').select(pairs.funding_source,pairs.project,latest.type)
summary=joined.group_by('funding_source').aggregate(projects=joined.project.nunique(),disaster=(joined.type=='disaster').fill_null(False).sum())
summary=summary.mutate(share=summary.disaster/summary.projects).order_by('funding_source')
result=summary.filter(summary.share>0.55).to_pyarrow().to_pylist()
OUT.joinpath('audit.json').write_text(json.dumps({'summary':summary.to_pyarrow().to_pylist(),'latest':latest.to_pyarrow().to_pylist(),'missing':joined.filter(joined.type.isnull()).to_pyarrow().to_pylist()},default=str,indent=2))
answer='; '.join(r['funding_source'] for r in result) or 'No funding sources meet the more-than-55% criterion as of 2022-11-01.'
OUT.joinpath('answer.json').write_text(json.dumps({'answer':answer}))
print(json.dumps(result,indent=2))
