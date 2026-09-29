import re,json
from pathlib import Path
import pandas as pd
OUT=Path('/workspace/work')
docs=pd.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
f=pd.read_parquet('/workspace/data/funding/Funding.parquet')
def norm(s):
    s=s.lower().replace('&',' ').replace('warningn','warning')
    s=re.sub(r'\([^)]*\)','',s)
    s=re.sub(r'[^a-z0-9]+','_',s).strip('_')
    s=re.sub(r'_(?:caljpia_fema|fema_caloes|caljpia|caloes|fema)(?:_project)?$','',s)
    s=re.sub(r'^202[12]_annual','annual',s)
    s=s.replace('storm_drain_trash_screens_phase_two','storm_drain_trash_screens')
    aliases={
    'citywide_guardrail_replacement':'guardrail_replacement_citywide',
    'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
    'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
    'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
    'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
    'malibu_bluffs_park_roof_replacement_project':'michael_landon_center_roof_replacement_project',
    'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
    'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
    'outdoor_warning_sirens_design':'outdoor_warning_sirens',
    'outdoor_warning_signs':'outdoor_warning_sirens',
    'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
    'trancas_canyon_park_playground_resurfacing':'trancas_playground_resurfacing',
    'trancas_canyon_park_playground':'trancas_playground_resurfacing',
    'trancas_canyon_park_upper_and_lower_slopes_repair':'trancas_canyon_park_slope_stabilization_project',
    'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
    'westward_beach_road_drainage_improvements_project':'westward_beach_road_shoulder_repairs',
    }
    return aliases.get(s,s)
f['project']=f.project_name.map(norm)
known=set(f.project)-{'discussion','recommended_action'}
rows=[]
heading=re.compile(r'^(Capital Improvement(?: and Disaster Recovery)? Projects|Disaster Projects)\s*\((Design|Construction|Completed|Not Started)\)',re.M)
for r in docs.itertuples():
    date=pd.to_datetime(re.search(r'Meeting date:\s*([^\n]+)',r.report_content).group(1))
    if r.report_id=='rid_0010': date=pd.Timestamp('2022-01-26')
    hs=list(heading.finditer(r.report_content))
    for i,h in enumerate(hs):
        body=r.report_content[h.end():hs[i+1].start() if i+1<len(hs) else len(r.report_content)]
        typ='capital' if h.group(1).startswith('Capital') else 'disaster'
        # Titles are standalone text lines, sometimes followed immediately by a bullet.
        for line in body.splitlines():
            project=norm(line)
            if project in known:
                rows.append(dict(project=project,report_date=date,report_id=r.report_id,type=typ,title=line.strip()))
reports=pd.DataFrame(rows).drop_duplicates(['project','report_date','type'])
assert not reports.duplicated(['project','report_date']).any(),reports[reports.duplicated(['project','report_date'],keep=False)]
f['grant_date']=pd.to_datetime(f.grant_time)
m=pd.merge_asof(f.sort_values('grant_date'),reports.sort_values('report_date'),left_on='grant_date',right_on='report_date',by='project',direction='backward')
m['year']=m.grant_date.dt.year
s=m.loc[m.type.eq('capital')].groupby('year').amount.sum()
y=int(s.idxmax()); amount=int(s.loc[y])
reports.to_csv(OUT/'extracted_reports.csv',index=False)
m.to_csv(OUT/'classified_funding.csv',index=False)
s.to_csv(OUT/'capital_totals.csv')
(OUT/'answer.json').write_text(json.dumps({'answer':f'{y}: ${amount:,} USD.'})+'\n')
print(s.to_string())
print('Names with no report:',sorted(known-set(reports.project)))
print('Unmatched funding by year:',m[m.type.isna()].groupby('year').amount.agg(['count','sum']).to_string())
print('Extracted reports:',len(reports))
