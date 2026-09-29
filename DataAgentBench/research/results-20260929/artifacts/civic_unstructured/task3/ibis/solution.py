import json,re
from pathlib import Path
import ibis
import pyarrow as pa

OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
fund=con.read_parquet('/workspace/data/funding/Funding.parquet')
docs=con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
cutoff=ibis.date('2022-08-01')

def norm(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')

# Alias groups based on agenda titles and descriptions. Separately listed
# projects remain distinct, including Birdview and Malibu Park drainage.
groups=[
 ['annual_street_maintenance','2021_annual_street_maintenance','2022_annual_street_maintenance'],
 ['storm_drain_trash_screens','storm_drain_trash_screens_phase_two'],
 ['citywide_guardrail_replacement','guardrail_replacement_citywide'],
 ['malibu_park_drainage_improvements','malibu_park_storm_drain_repairs'],
 ['broad_beach_road_water_quality_infrastructure_repairs','broad_beach_road_water_quality_repair'],
 ['clover_heights_storm_drain','clover_heights_storm_drainage_improvements'],
 ['encinal_canyon_road_drainage_improvements','encinal_canyon_road_repairs'],
 ['latigo_canyon_road_roadway_retaining_wall_improvements','latigo_canyon_road_retaining_wall_repair_project'],
 ['malibu_bluffs_park_south_walkway','malibu_bluffs_park_south_walkway_repairs'],
 ['outdoor_warning_sirens','outdoor_warningn_sirens_design','outdoor_warning_sirens_design','outdoor_warning_signs'],
 ['pch_overhead_warning_signs','pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch'],
 ['point_dume_decomposed_granite_walkway_repair_project','point_dume_walkway_repairs'],
 ['trancas_playground_resurfacing','trancas_canyon_park_playground_resurfacing','trancas_canyon_park_playground'],
 ['trancas_canyon_park_slope_stabilization_project','trancas_canyon_park_upper_and_lower_slopes_repair'],
 ['westward_beach_road_improvements_project','westward_beach_road_repair_project'],
 ['westward_beach_road_shoulder_repairs','westward_beach_road_drainage_improvements_project'],
 ['michael_landon_center_roof_replacement_project','malibu_bluffs_park_roof_replacement_project'],
]
alias={v:g[0] for g in groups for v in g}
def canonical(s):
    s=norm(s)
    s=re.sub(r'_(?:(?:fema|caloes|caljpia)_?)+(?:project)?$','',s)
    return alias.get(s,s)

names=fund.select('project_name').distinct().to_pyarrow().to_pylist()
lookup={r['project_name']:canonical(r['project_name']) for r in names if r['project_name'] not in {'discussion','recommended_action'}}
valid=set(lookup.values())
rows=[]; dates=[]
section=re.compile(r'(?:Capital Improvement(?: and Disaster Recovery)?|Disaster(?: Recovery)?) Projects\s*\((Design|Construction|Completed|Not Started)\)',re.I)
for doc in docs.to_pyarrow().to_pylist():
    text=doc['report_content']; rid=doc['report_id']
    date=re.search(r'Meeting date:\s*([^\n]+)',text).group(1).strip()
    if rid=='rid_0010': date='January 26, 2022'
    # Normalize abbreviated month so DuckDB handles all report dates alike.
    date=re.sub(r'^Jun ', 'June ', date)
    dates.append({'report_id':rid,'date_text':date})
    status=None
    for pos,line in enumerate(text.splitlines()):
        m=section.search(line)
        if m:
            status=m.group(1).lower()
            line=line[m.end():]
        key=canonical(line)
        if status and key in valid:
            rows.append({'report_id':rid,'project':key,'status':status,'position':pos,'title':line.strip()})

reports=con.create_table('reports',ibis.memtable(pa.Table.from_pylist(dates)))
reports=reports.mutate(report_date=reports.date_text.as_timestamp('%B %d, %Y').date())
observations=con.create_table('observations',ibis.memtable(pa.Table.from_pylist(rows)))
history=observations.join(reports,'report_id').filter(ibis._.report_date<=cutoff)
# In rid_0010 a few old entries recur later in the completed section;
# prefer that later explicit section when the same entity occurs twice.
w=ibis.window(group_by='project',order_by=[ibis.desc('report_date'),ibis.desc('position')])
latest=history.mutate(rn=ibis.row_number().over(w)).filter(ibis._.rn==0).select('project','status','report_date','report_id')
mapping=con.create_table('aliases',ibis.memtable(pa.Table.from_pylist([{'project_name':k,'project':v} for k,v in lookup.items()])))
eligible=fund.mutate(grant_date=fund.grant_time.cast('date')).filter(ibis._.grant_date<=cutoff)
projects=eligible.join(mapping,'project_name').select('funding_source','project').distinct()
joined=projects.left_join(latest,'project')
summary=joined.group_by('funding_source').aggregate(total_projects=ibis._.project.nunique(),completed_projects=(ibis._.status=='completed').fill_null(False).cast('int64').sum())
result=summary.filter(summary.completed_projects*4>=summary.total_projects).order_by('funding_source')
answer=result.to_pyarrow().to_pylist()
(OUT/'answer.json').write_text(json.dumps({'answer':('; '.join(r['funding_source'] for r in answer) if answer else 'No funding sources meet the 25% threshold as of 2022-08-01.')},indent=2)+'\n')
(OUT/'audit.json').write_text(json.dumps({'sources':summary.order_by('funding_source').to_pyarrow().to_pylist(),'latest_statuses':latest.order_by('project').to_pyarrow().to_pylist(),'extracted_observations':rows},indent=2,default=str))
print(json.dumps(answer,indent=2))
print('Latest statuses:',latest.order_by('project').to_pyarrow().to_pylist())
print('Names never matched:', sorted(valid-{r['project'] for r in rows}))
