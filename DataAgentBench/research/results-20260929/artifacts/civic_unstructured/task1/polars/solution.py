import re,json
from datetime import datetime,date
from pathlib import Path
import polars as pl
OUT=Path('/workspace/work')
CUTOFF=date(2023,1,1)
def norm(s):
    return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def canonical(s):
    s=norm(s)
    s=re.sub(r'_(?:fema_caloes|caljpia_fema|caljpia|caloes|fema)(?:_project)?$','',s)
    if re.fullmatch(r'(?:20\d\d_)?annual_street_maintenance',s): return 'annual_street_maintenance'
    aliases={
        'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
        'westward_beach_road_improvements_project':'westward_beach_road_repair_project',
        'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
        'trancas_playground_resurfacing':'trancas_canyon_park_playground_resurfacing',
        'trancas_canyon_park_playground':'trancas_canyon_park_playground_resurfacing',
        'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
        'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
        'outdoor_warning_sirens_design':'outdoor_warning_sirens',
        'outdoor_warning_signs':'outdoor_warning_sirens',
        'citywide_guardrail_replacement':'guardrail_replacement_citywide',
        'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
        'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
        'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
        'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
        'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
    }
    return aliases.get(s,s)
docs=pl.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
funding=pl.read_parquet('/workspace/data/funding/Funding.parquet')
names=set(funding['project_name'])-{'discussion','recommended_action'}
rows=[]
for r in docs.iter_rows(named=True):
    content=r['report_content']
    dt=datetime.strptime(re.search(r'Commission Meeting\s+(\d\d-\d\d-\d\d)',content)[1],'%m-%d-%y').date()
    if r['report_id']=='rid_0010': dt=date(2022,1,26) # Explicit supplied correction
    if dt>CUTOFF: continue
    lines=content.splitlines()
    typ=status=None
    for i,line in enumerate(lines):
        section=re.fullmatch(r'\s*(Capital Improvement|Disaster) Projects \((Design|Construction|Completed|Not Started)\)\s*',line)
        if section:
            typ='capital' if section[1]=='Capital Improvement' else 'disaster'
            status=section[2].lower()
        if typ is None: continue
        # Exact whole-title matches, including titles wrapped over two lines.
        for n in (1,2):
            title=' '.join(lines[i:i+n]).strip()
            key=norm(title)
            if key in names:
                rows.append({'project':canonical(key),'title':title,'date':dt,'report_id':r['report_id'],'type':typ,'status':status})
                break
reports=pl.DataFrame(rows).unique()
reports.write_csv(OUT/'extracted_reports.csv')
latest=reports.sort('date').group_by('project',maintain_order=True).last()
totals=(funding.with_columns(pl.col('grant_time').str.to_date(),pl.col('project_name').map_elements(canonical,return_dtype=pl.String).alias('project'))
        .filter(pl.col('grant_time')<=CUTOFF).group_by('project').agg(pl.col('amount').sum().alias('total_funding')))
latest=latest.join(totals,on='project',how='left').sort('project')
latest.write_csv(OUT/'latest_projects.csv')
result=latest.filter((pl.col('type')=='capital')&(pl.col('status')=='design')&(pl.col('total_funding')>500000))
result.write_csv(OUT/'qualifying_projects.csv')
answer='; '.join(f"{r['title']} (${r['total_funding']:,})" for r in result.iter_rows(named=True))+'.'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(result.select('title','date','total_funding'))
print(answer)
