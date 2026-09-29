import re,json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import ibis

OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
docs=con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
fund=con.read_parquet('/workspace/data/funding/Funding.parquet')

def normalize(name):
    name=re.sub(r'\(.*','',name)
    name=re.sub(r'[^a-z0-9]+','_',name.lower()).strip('_')
    name=re.sub(r'_(?:caljpia_fema|fema_caloes|fema|caloes|caljpia)_project$','',name)
    name=re.sub(r'_fema$','',name)
    return name

# Entity aliases established from the agenda titles and descriptions.
# Separately listed projects (e.g. Birdview and Malibu Park) remain distinct.
groups=[
 ['annual_street_maintenance','2021_annual_street_maintenance','2022_annual_street_maintenance'],
 ['storm_drain_trash_screens','storm_drain_trash_screens_phase_two'],
 ['citywide_guardrail_replacement','guardrail_replacement_citywide'],
 ['malibu_park_drainage_improvements','malibu_park_storm_drain_repairs'],
 ['broad_beach_road_water_quality_infrastructure_repairs','broad_beach_road_water_quality_repair'],
 ['clover_heights_storm_drain','clover_heights_storm_drainage_improvements'],
 ['encinal_canyon_road_drainage_improvements','encinal_canyon_road_repairs'],
 ['latigo_canyon_road_roadway_retaining_wall_improvements','latigo_canyon_road_retaining_wall_repair_project'],
 ['outdoor_warning_sirens','outdoor_warning_sirens_design','outdoor_warningn_sirens_design','outdoor_warning_signs'],
 ['westward_beach_road_improvements_project','westward_beach_road_repair_project'],
 ['westward_beach_road_shoulder_repairs','westward_beach_road_drainage_improvements_project'],
 ['malibu_bluffs_park_south_walkway','malibu_bluffs_park_south_walkway_repairs'],
 ['trancas_playground_resurfacing','trancas_canyon_park_playground_resurfacing','trancas_canyon_park_playground'],
 ['point_dume_decomposed_granite_walkway_repair_project','point_dume_walkway_repairs'],
 ['michael_landon_center_roof_replacement_project','malibu_bluffs_park_roof_replacement_project'],
]
alias={x:g[0] for g in groups for x in g}
def canonical(s):
    n=normalize(s)
    return alias.get(n,n)

fund_names=fund.select('project_name').distinct().to_pyarrow().to_pylist()
known={normalize(r['project_name']) for r in fund_names} - {'discussion','recommended_action'}
rows=[]
for doc in docs.to_pyarrow().to_pylist():
    text=doc['report_content']; rid=doc['report_id']
    date=re.search(r'Meeting date:\s*([^\n]+)',text)[1].strip()
    if rid=='rid_0010':date='January 26, 2022'
    # Normalize abbreviated month for Ibis parsing below.
    if date.startswith('Jun '):date=date.replace('Jun ','June ',1)
    status=None
    for line in text.splitlines():
        line=line.strip()
        section=re.fullmatch(r'(?:Capital Improvement(?: and Disaster Recovery)?|Disaster) Projects \((Design|Construction|Completed|Not Started)\)',line)
        if section:
            status=section[1].lower()
        elif status and normalize(line) in known:
            rows.append({'report_id':rid,'meeting_date':date,'title':line,'project':canonical(line),'status':status})
(OUT/'extracted_projects.json').write_text(json.dumps(rows,indent=2))
obs=con.create_table('observations',ibis.memtable(rows))
obs=obs.mutate(date=obs.meeting_date.as_timestamp('%B %d, %Y').date())
start=ibis.date('2021-06-01'); end=ibis.date('2023-01-01')
obs=obs.filter(obs.date.between(start,end))
# Explicitly require distinct reports as well as distinct statuses.
a=obs; b=obs.view()
changed=a.join(b,(a.project==b.project)&(a.report_id!=b.report_id)&(a.status!=b.status)).select(a.project).distinct()
mapping=con.create_table('aliases',ibis.memtable([{'project_name':r['project_name'],'project':canonical(r['project_name'])} for r in fund_names if normalize(r['project_name']) in known]))
f=fund.mutate(date=fund.grant_time.cast('date'))
f=f.filter(f.date.between(start,end)).join(mapping,'project_name')
totals=f.group_by('project').aggregate(total=f.amount.sum())
result=changed.left_join(totals,'project').select(changed.project,total=totals.total.fill_null(0))
audit=result.order_by('project').to_pyarrow().to_pylist()
(OUT/'funding_by_project.json').write_text(json.dumps(audit,indent=2))
summary=result.aggregate(total=result.total.sum(),projects=result.count()).to_pyarrow().to_pylist()[0]
avg=(Decimal(summary['total'])/Decimal(summary['projects'])).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
(OUT/'answer.json').write_text(json.dumps({'answer':f'${avg:,.2f} USD'}))
print(json.dumps({'summary':summary,'average':str(avg),'projects':audit},indent=2))
