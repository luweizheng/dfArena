import re,json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import ibis
import pyarrow as pa

OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
docs=con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
fund=con.read_parquet('/workspace/data/funding/Funding.parquet')

def normalize(s):
    s=re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
    s=re.sub(r'_(?:caljpia_fema|fema_caloes|caljpia|caloes|fema)(?:_project)?$','',s)
    s=re.sub(r'^202[12]_annual_street','annual_street',s)
    aliases={
      'storm_drain_trash_screens_phase_two':'storm_drain_trash_screens',
      'pch_crosswalk_improvements_at_big_rock_drive_and_20326_pch':'pch_overhead_warning_signs',
      'guardrail_replacement_citywide':'citywide_guardrail_replacement',
      'malibu_park_storm_drain_repairs':'malibu_park_drainage_improvements',
      'outdoor_warningn_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_sirens_design':'outdoor_warning_sirens',
      'outdoor_warning_signs':'outdoor_warning_sirens',
      'broad_beach_road_water_quality_repair':'broad_beach_road_water_quality_infrastructure_repairs',
      'clover_heights_storm_drainage_improvements':'clover_heights_storm_drain',
      'encinal_canyon_road_repairs':'encinal_canyon_road_drainage_improvements',
      'latigo_canyon_road_retaining_wall_repair_project':'latigo_canyon_road_roadway_retaining_wall_improvements',
      'malibu_bluffs_park_south_walkway_repairs':'malibu_bluffs_park_south_walkway',
      'trancas_canyon_park_playground':'trancas_playground_resurfacing',
      'trancas_canyon_park_playground_resurfacing':'trancas_playground_resurfacing',
      'point_dume_walkway_repairs':'point_dume_decomposed_granite_walkway_repair_project',
      'westward_beach_road_repair_project':'westward_beach_road_improvements_project',
      'westward_beach_road_drainage_improvements_project':'westward_beach_road_shoulder_repairs',
    }
    return aliases.get(s,s)

names=fund.select('project_name').distinct().to_pyarrow().to_pylist()
name_map=[{'project_name':r['project_name'],'project':normalize(r['project_name'])} for r in names]
known={r['project'] for r in name_map}-{ 'discussion','recommended_action'}
# Date strings are parsed and filtered by Ibis before document text extraction.
dated=docs.mutate(report_date=docs.report_content.re_extract(r'Meeting date: ([^\n\r]+)',1))
dated=dated.mutate(report_date=ibis.ifelse(dated.report_id=='rid_0010','January 26, 2022',dated.report_date).replace('Jun ', 'June ').as_timestamp('%B %d, %Y').date())
# Normalize the abbreviated month in the June 2023 header before parsing.
dated=dated.filter(dated.report_date<=ibis.date('2022-06-01'))
records=[]
for r in dated.to_pyarrow().to_pylist():
    kind=None
    for line in r['report_content'].splitlines():
        line=line.strip()
        section=re.match(r'(Capital Improvement|Disaster) Projects \(([^)]+)\)',line)
        if section:
            kind='capital' if section[1]=='Capital Improvement' else 'disaster'
            line=line[section.end():].strip()
        if kind:
            title=line.split('(cid:')[0].strip()
            key=normalize(title)
            if key in known:
                records.append({'project':key,'report_date':r['report_date'],'type':kind,'report_id':r['report_id'],'title':title})
reports=ibis.memtable(pa.Table.from_pylist(records))
map_table=ibis.memtable(pa.Table.from_pylist(name_map))
# Preserve every funding row; fid is documented as unique.
assert fund.count().to_pyarrow().as_py()==fund.select('fid').distinct().count().to_pyarrow().as_py()
f=fund.mutate(grant_date=fund.grant_time.cast('date'))
f=f.filter(f.grant_date.between(ibis.date('2021-06-01'),ibis.date('2022-06-01')))
f=f.join(map_table,'project_name').select(f,map_table.project)
candidates=f.join(reports,[f.project==reports.project,f.grant_date>=reports.report_date]).select(f,reports.report_date,reports.type,reports.report_id)
w=ibis.window(group_by='fid',order_by=ibis.desc('report_date'))
latest=candidates.mutate(rn=ibis.row_number().over(w)).filter(lambda t:t.rn==0)
totals=latest.group_by('type').aggregate(total=latest.amount.sum()).order_by('type')
rows=totals.to_pyarrow().to_pylist()
values={r['type']:r['total'] for r in rows}
ratio=(Decimal(values['capital'])/Decimal(values['disaster'])).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
(OUT/'answer.json').write_text(json.dumps({'answer':str(ratio)}))
(OUT/'extracted_reports.json').write_text(json.dumps(records,default=str,indent=2))
latest.order_by('project','grant_date').to_parquet(OUT/'classified_funding.parquet')
unmatched=f.anti_join(latest.select('fid'),'fid').group_by('project_name').aggregate(n=ibis._.count()).order_by('project_name')
print('TOTALS',rows,'RATIO',ratio)
print('UNMATCHED',unmatched.to_pyarrow().to_pylist())
print('HISTORIES',reports.group_by(['project','type']).aggregate(n=ibis._.count()).order_by('project','type').to_pyarrow().to_pylist())
