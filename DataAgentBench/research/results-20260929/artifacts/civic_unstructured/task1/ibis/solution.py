import json
import re
from pathlib import Path
import ibis

ROOT = Path('/workspace/work')
con = ibis.duckdb.connect()
docs = con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
funding = con.read_parquet('/workspace/data/funding/Funding.parquet')
cutoff = ibis.date('2023-01-01')

def normalize(s):
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

# Semantic aliases established from the agenda project titles/descriptions.
# Disaster funding suffixes identify the sponsor, not a separate civic project.
def canonical(name):
    n = re.sub(r'_(?:fema_caloes|caljpia_fema|caljpia|caloes|fema)(?:_project)?$', '', name)
    n = re.sub(r'^20\d\d_annual_street_maintenance$', 'annual_street_maintenance', n)
    aliases = {
        'storm_drain_trash_screens_phase_two': 'storm_drain_trash_screens',
        'westward_beach_road_improvements_project': 'westward_beach_road_repair_project',
        'westward_beach_road_shoulder_repairs': 'westward_beach_road_drainage_improvements_project',
        'malibu_bluffs_park_roof_replacement_project': 'michael_landon_center_roof_replacement_project',
        'trancas_playground_resurfacing': 'trancas_canyon_park_playground_resurfacing',
        'trancas_canyon_park_playground': 'trancas_canyon_park_playground_resurfacing',
        'malibu_bluffs_park_south_walkway_repairs': 'malibu_bluffs_park_south_walkway',
        'point_dume_walkway_repairs': 'point_dume_decomposed_granite_walkway_repair_project',
        'outdoor_warningn_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_signs': 'outdoor_warning_sirens',
        'clover_heights_storm_drainage_improvements': 'clover_heights_storm_drain',
        'encinal_canyon_road_repairs': 'encinal_canyon_road_drainage_improvements',
        'broad_beach_road_water_quality_repair': 'broad_beach_road_water_quality_infrastructure_repairs',
        'latigo_canyon_road_retaining_wall_repair_project': 'latigo_canyon_road_roadway_retaining_wall_improvements',
        'trancas_canyon_park_upper_and_lower_slopes_repair': 'trancas_canyon_park_slope_stabilization_project',
        'citywide_guardrail_replacement': 'guardrail_replacement_citywide',
        'malibu_park_storm_drain_repairs': 'malibu_park_drainage_improvements',
    }
    return aliases.get(n, n)

names = funding.select('project_name').distinct().to_pyarrow()['project_name'].to_pylist()
known = set(names) - {'discussion', 'recommended_action'}
# Parse textual metadata, then perform temporal and relational work in Ibis.
records = []
section_re = re.compile(r'^(Capital Improvement|Disaster) Projects\s*\((Design|Construction|Completed|Not Started)\)$', re.I)
for doc in docs.to_pyarrow().to_pylist():
    content = doc['report_content']
    date_text = re.search(r'Meeting date:\s*([^\n]+)', content).group(1).strip()
    date_text = re.sub(r'^Jun ', 'June ', date_text)
    if doc['report_id'] == 'rid_0010':
        date_text = 'January 26, 2022'  # Explicit source correction supplied in hints.
    content = re.sub(r'Page \d+ of \d+\s*Agenda Item[^\n]*', '', content)
    lines = [x.strip() for x in content.splitlines() if x.strip()]
    category = status = None
    for i, line in enumerate(lines):
        section = section_re.fullmatch(line)
        if section:
            category = 'capital' if section[1].lower().startswith('capital') else 'disaster'
            status = section[2].lower()
            continue
        # Combined sections occur only after this question's cutoff.
        if re.match(r'Capital Improvement and Disaster Recovery Projects', line):
            category = status = None
        if category is None:
            continue
        for width in (1, 2, 3):
            title = ' '.join(lines[i:i+width])
            key = normalize(title)
            if key in known:
                records.append(dict(project=canonical(key), project_title=title,
                    report_id=doc['report_id'], report_date_text=date_text,
                    type=category, status=status))
                break

reports = ibis.memtable(records)
reports = reports.mutate(report_date=reports.report_date_text.as_timestamp('%B %d, %Y').date())
eligible = reports.filter(reports.report_date <= cutoff)
w = ibis.window(group_by='project', order_by=[ibis.desc('report_date'), ibis.desc('report_id')])
latest = eligible.mutate(rank=ibis.row_number().over(w)).filter(lambda t: t.rank == 0)
latest = latest.filter((latest.type == 'capital') & (latest.status == 'design'))
alias_table = ibis.memtable([{'project_name': n, 'project': canonical(n)} for n in names if n in known])
f = funding.mutate(grant_date=funding.grant_time.cast('date'))
f = f.filter(f.grant_date <= cutoff).join(alias_table, 'project_name')
totals = f.group_by('project').aggregate(total_funding=f.amount.sum())
result = latest.join(totals, 'project').filter(lambda t: t.total_funding > 500000)
result = result.select('project', 'project_title', 'total_funding', 'report_id', 'report_date').order_by('project')
rows = result.to_pyarrow().to_pylist()
(ROOT / 'qualifying_projects.json').write_text(json.dumps(rows, default=str, indent=2))
(ROOT / 'extracted_reports.json').write_text(json.dumps(records, indent=2))
answer = '; '.join(('Annual Street Maintenance' if r['project'] == 'annual_street_maintenance' else r['project_title']) + f" (${r['total_funding']:,})" for r in rows) + '.'
(ROOT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps(rows, default=str, indent=2))
