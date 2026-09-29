import json
import re
from pathlib import Path
import ibis
import pyarrow as pa

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
ibis.set_backend(con)
docs = con.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
funding = con.read_parquet('/workspace/data/funding/Funding.parquet')
cutoff = ibis.date('2022-11-01')
# Text extraction is the nonrelational boundary. Dates and all subsequent
# filtering, latest-record selection, joins, and sums are Ibis expressions.
section = re.compile(r'^(Capital Improvement(?: and Disaster Recovery)?|Disaster) Projects\s*\((Design|Construction|Completed|Not Started)\)\s*$', re.I)
def normalize(s):
    s = re.sub(r'\([^)]*\)', '', s)
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

def canonical(s):
    s = normalize(s)
    s = re.sub(r'_(?:fema_caloes|caloes|fema|caljpia)(?:_project)?$', '', s)
    if s.startswith('clover_heights_storm_drain'):
        return 'clover_heights_storm_drain'
    if s == 'encinal_canyon_road_repairs':
        return 'encinal_canyon_road_drainage_improvements'
    if s.startswith('outdoor_warning'):
        return 'outdoor_warning_sirens'
    if s == 'westward_beach_road_drainage_improvements_project':
        return 'westward_beach_road_shoulder_repairs'
    return s

raw = docs.to_pyarrow().to_pylist()
# Discover the complete candidate universe from actual disaster/not-started
# sections, rather than prespecifying eligible projects.
candidates = set()
for doc in raw:
    state = None
    for line in doc['report_content'].splitlines():
        line = line.strip()
        m = section.match(line)
        if m:
            state = (m[1].lower(), m[2].lower())
        elif state == ('disaster', 'not started') and re.search(r'\((?:FEMA|CalOES)', line):
            candidates.add(canonical(line))

records = []
for doc in raw:
    text = doc['report_content']
    date = re.search(r'Meeting date:\s*([^\n]+)', text, re.I)[1].strip()
    if doc['report_id'] == 'rid_0010':
        date = 'January 26, 2022'  # Explicit correction in supplied hints.
    date = date.replace('Jun ', 'June ')
    state = None
    for line in text.splitlines():
        line = line.strip()
        m = section.match(line)
        if m:
            state = ('disaster' if m[1].lower() == 'disaster' else 'capital', m[2].lower())
            continue
        key = canonical(line)
        if state and key in candidates:
            records.append(dict(project=key, report_id=doc['report_id'], date_text=date,
                                type=state[0], status=state[1], heading=line))
reports = ibis.memtable(pa.Table.from_pylist(records))
reports = reports.mutate(report_date=reports.date_text.as_timestamp('%B %d, %Y').date())
reports = reports.filter(reports.report_date <= cutoff)
latest = reports.mutate(rank=ibis.row_number().over(ibis.window(group_by='project', order_by=[ibis.desc('report_date'), ibis.desc('report_id')]))).filter(ibis._.rank == 0)
aliases = [dict(project_name=r['project_name'], project=canonical(r['project_name']))
           for r in funding.select('project_name').distinct().to_pyarrow().to_pylist()]
aliases = ibis.memtable(pa.Table.from_pylist(aliases))
f = funding.mutate(grant_date=funding.grant_time.cast('date'))
f = f.filter(f.grant_date <= cutoff).join(aliases, 'project_name')
totals = f.group_by('project').aggregate(total_funding=f.amount.sum())
result = latest.filter((latest.type == 'disaster') & (latest.status == 'not started')).join(totals, 'project')
result = result.filter(result.total_funding > 1_000_000).select('project', 'total_funding').order_by('project')
rows = result.to_pyarrow().to_pylist()
audit = latest.join(totals, 'project').select('project', 'report_id', 'report_date', 'type', 'status', 'total_funding').order_by('project').to_pyarrow().to_pylist()
(OUT / 'audit.json').write_text(json.dumps(audit, indent=2, default=str))
answer = '; '.join(f"{r['project'].replace('_', ' ').title()} (${r['total_funding']:,})" for r in rows) if rows else 'No projects meet all the specified criteria as of 2022-11-01.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps({'answer': answer}))
print(json.dumps(audit, indent=2, default=str))
