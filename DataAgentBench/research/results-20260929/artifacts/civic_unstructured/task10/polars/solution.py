import json,re
from datetime import datetime,date
from pathlib import Path
import polars as pl

OUT=Path('/workspace/work')
fund=pl.read_parquet('/workspace/data/funding/Funding.parquet')
docs=pl.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
def norm(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
# Name equivalences established from agenda headings and project descriptions.
aliases={
 'guardrail_replacement_citywide':'citywide_guardrail_replacement',
 'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
 'trancas_playground_resurfacing':'trancas_canyon_park_playground',
 'trancas_canyon_park_playground_resurfacing':'trancas_canyon_park_playground',
 'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
 'pch_overhead_warning_signs':'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch',
 'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
 'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
 'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
 'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
 'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
 'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
 'outdoor_warning_signs':'outdoor_warning_sirens',
 'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
 'outdoor_warning_sirens_design':'outdoor_warning_sirens',
 'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
 '2021_annual_street_maintenance':'annual_street_maintenance',
 '2022_annual_street_maintenance':'annual_street_maintenance',
}
def canonical(s):
    s=norm(s)
    s=re.sub(r'_(?:caljpia_fema|fema_caloes|fema|caloes|caljpia)(?:_project)?$','',s)
    return aliases.get(s,s)

names=set(fund['project_name'])-{'discussion','recommended_action'}
rows=[]
for doc in docs.iter_rows(named=True):
    text=doc['report_content']
    ds=re.search(r'Meeting date:\s*([^\n]+)',text).group(1).strip()
    try: dt=datetime.strptime(ds,'%B %d, %Y').date()
    except ValueError: dt=datetime.strptime(ds,'%b %d, %Y').date()
    if doc['report_id']=='rid_0010': dt=date(2022,1,26)
    if dt>date(2022,9,1): continue
    status=None
    for line_no,line in enumerate(text.splitlines()):
        line=line.strip()
        heading=re.search(r'Projects\s*\((Design|Construction|Completed|Not Started)\)',line,re.I)
        if heading:
            status=heading.group(1).lower()
        elif status and norm(line) in names:
            rows.append({'project':canonical(line),'report_date':dt,'status':status,
                         'report_id':doc['report_id'],'heading':line,'line':line_no})
reports=pl.DataFrame(rows)
# A repeated alias in the same report is resolved by its final section entry.
# In rid_0010 the final Completed entries restate the guardrail and Malibu Park projects.
reports=reports.sort(['report_date','line']).unique(['project','report_date'],keep='last',maintain_order=True)
reports.write_csv(OUT/'status_history.csv')
fund=fund.with_columns(pl.col('grant_time').str.to_date(),pl.col('project_name').map_elements(canonical,return_dtype=pl.String).alias('project'))
fund=fund.filter(pl.col('grant_time').is_between(date(2021,9,1),date(2022,9,1),closed='both') & ~pl.col('project_name').is_in(['discussion','recommended_action']))
matched=fund.sort('grant_time').join_asof(reports.sort('report_date'),left_on='grant_time',right_on='report_date',by='project',strategy='backward',check_sortedness=False)
matched.write_csv(OUT/'funding_status_audit.csv')
totals=matched.group_by('status').agg(pl.col('amount').sum()).sort('status')
print(totals)
print('Unmatched:',matched.filter(pl.col('status').is_null()).select('project_name','grant_time','amount'))
completed=matched.filter(pl.col('status')=='completed')['amount'].sum()
not_started=matched.filter(pl.col('status')=='not started')['amount'].sum()
assert not_started>0
answer=f'{completed/not_started:.2f}'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(answer)
