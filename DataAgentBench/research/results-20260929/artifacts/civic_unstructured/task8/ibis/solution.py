import json, re
from pathlib import Path
import ibis
import pyarrow as pa

ROOT = Path('/workspace/work')
con = ibis.duckdb.connect()
ibis.set_backend(con)
docs = con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet', table_name='civic_docs')
fund = con.read_parquet('/workspace/data/funding/Funding.parquet', table_name='funding')
cutoff = ibis.date('2022-06-01')

def norm(s):
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

def canonical(s):
    s = re.sub(r'_(?:fema_caloes|caljpia_fema|caljpia|fema|caloes)_project$', '', s)
    s = re.sub(r'^20\d\d_annual_street_maintenance$', 'annual_street_maintenance', s)
    aliases = {
        'storm_drain_trash_screens_phase_two': 'storm_drain_trash_screens',
        'malibu_park_storm_drain_repairs': 'malibu_park_drainage_improvements',
        'guardrail_replacement_citywide': 'citywide_guardrail_replacement',
        'clover_heights_storm_drainage_improvements': 'clover_heights_storm_drain',
        'point_dume_decomposed_granite_walkway_repair_project': 'point_dume_walkway_repairs',
        'trancas_playground_resurfacing': 'trancas_canyon_park_playground',
        'trancas_canyon_park_playground_resurfacing': 'trancas_canyon_park_playground',
        'malibu_bluffs_park_south_walkway_repairs': 'malibu_bluffs_park_south_walkway',
        'outdoor_warningn_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_fema': 'outdoor_warning_sirens',
    }
    return aliases.get(s, s)

names = fund.select('project_name').distinct().to_pyarrow().column('project_name').to_pylist()
name_set = set(names)
# Text extraction only: relational filtering, dates, latest reports, and sums use Ibis.
rows = []
section_re = re.compile(r'^(Capital Improvement|Disaster) Projects \((Design|Construction|Completed|Not Started)\)$', re.I)
for doc in docs.to_pyarrow().to_pylist():
    content = doc['report_content']
    date = re.search(r'Meeting date:\s*([^\n]+)', content)[1].strip()
    if doc['report_id'] == 'rid_0010':
        date = 'January 26, 2022'  # Explicit correction in the supplied hints.
    kind = status = None
    lines = content.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        section = section_re.match(line)
        if section:
            kind = 'capital' if section[1].lower().startswith('capital') else 'disaster'
            status = section[2].lower()
            continue
        if not kind:
            continue
        key = norm(line)
        if key in name_set and key not in {'discussion', 'recommended_action'}:
            rows.append(dict(report_id=doc['report_id'], date_text=re.sub(r'^Jun ', 'June ', date),
                             project=canonical(key), title=line, type=kind, status=status))

reports = ibis.memtable(pa.Table.from_pylist(rows))
reports = reports.mutate(report_date=reports.date_text.as_timestamp('%B %d, %Y').date())
reports = reports.filter(reports.report_date <= cutoff)
w = ibis.window(group_by='project', order_by=ibis.desc('report_date'))
latest = reports.mutate(rank=ibis.row_number().over(w)).filter(lambda t: t.rank == 0)
eligible = latest.filter((latest.type == 'capital') & (latest.status == 'construction'))
lookup = ibis.memtable(pa.Table.from_pylist([
    {'project_name': n, 'project': canonical(n)} for n in names
]))
f = fund.mutate(grant_date=fund.grant_time.cast('date'))
f = f.filter(f.grant_date <= cutoff).join(lookup, 'project_name')
totals = f.group_by('project').aggregate(total_funding=f.amount.sum())
result = eligible.left_join(totals, 'project').select(
    eligible.project, eligible.title, eligible.report_id, eligible.report_date,
    total_funding=totals.total_funding.fill_null(0)
).order_by('total_funding', 'project')
records = result.to_pyarrow().to_pylist()
(ROOT / 'eligible_projects.json').write_text(json.dumps(records, default=str, indent=2))
assert records, 'No eligible projects found'
best = records[0]
answer = f"{best['title']}: ${best['total_funding']:,} USD."
(ROOT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps(records, default=str, indent=2))
