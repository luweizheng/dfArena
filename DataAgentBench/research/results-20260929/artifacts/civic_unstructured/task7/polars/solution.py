import re
import json
from datetime import datetime, date
from pathlib import Path
import polars as pl

ROOT = Path('/workspace')
OUT = ROOT / 'work'
CUTOFF = date(2022, 11, 1)

def canonical(name):
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    name = re.sub(r'_(?:fema_caloes|caljpia_fema|fema|caloes|caljpia)(?:_project)?$', '', name)
    name = name.replace('outdoor_warningn_', 'outdoor_warning_')
    if name.startswith('outdoor_warning_'):
        return 'outdoor_warning_sirens'
    if name in ('clover_heights_storm_drainage_improvements', 'clover_heights_storm_drain'):
        return 'clover_heights_storm_drain'
    if re.fullmatch(r'(?:\d{4}_)?annual_street_maintenance', name):
        return 'annual_street_maintenance'
    if name == 'storm_drain_trash_screens_phase_two':
        return 'storm_drain_trash_screens'
    return name

section_re = re.compile(r'^(Capital Improvement|Disaster) Projects \((Design|Construction|Completed|Not Started)\)\s*$', re.M)
docs = pl.read_parquet(ROOT / 'data/civic_docs/civic_docs.parquet')
sections = []
for report in docs.iter_rows(named=True):
    text = report['report_content']
    header = re.search(r'Commission Meeting\s+(\d{2}-\d{2}-\d{2})', text).group(1)
    meeting_date = datetime.strptime(header, '%m-%d-%y').date()
    if report['report_id'] == 'rid_0010':
        meeting_date = date(2022, 1, 26)  # Explicit correction in supplied hints.
    if meeting_date > CUTOFF:
        continue
    # Remove pagination before extracting standalone project headings.
    text = re.sub(r'Page \d+ of \d+\s*Agenda Item #[^\n]*', '', text)
    headers = list(section_re.finditer(text))
    for i, match in enumerate(headers):
        body = text[match.end():headers[i+1].start() if i+1 < len(headers) else len(text)]
        sections.append((report['report_id'], meeting_date,
                         'disaster' if match[1] == 'Disaster' else 'capital',
                         match[2].lower(), body))

# Every possible match must have appeared in a disaster/not-started section.
# Extract that complete candidate universe, then look for each candidate in ALL
# subsequent sections, including changed statuses and types.
candidates = {}
for rid, dt, kind, status, body in sections:
    if (kind, status) != ('disaster', 'not started'):
        continue
    for match in re.finditer(r'^([^\n]+)\n\s*\(cid:190\) Project Description:', body, re.M):
        title = match[1].strip()
        candidates[canonical(title)] = re.sub(r'\s*\([^)]*\)', '', title).strip()
assert candidates, 'No candidate headings extracted'

records = []
for rid, dt, kind, status, body in sections:
    for line in body.splitlines():
        key = canonical(line.strip())
        if key in candidates:
            records.append(dict(project=key, report_id=rid, report_date=dt, type=kind, status=status))
reports = pl.DataFrame(records).unique()
latest = reports.sort('report_date').group_by('project').last()
funding = (pl.read_parquet(ROOT / 'data/funding/Funding.parquet')
           .with_columns(pl.col('grant_time').str.to_date(),
                         pl.col('project_name').map_elements(canonical, return_dtype=pl.String).alias('project'))
           .filter((pl.col('grant_time') <= CUTOFF) & pl.col('project').is_in(list(candidates)))
           .group_by('project').agg(pl.col('amount').sum().alias('total_funding')))
audit = latest.join(funding, on='project', how='left').sort('project')
result = audit.filter((pl.col('type') == 'disaster') & (pl.col('status') == 'not started') & (pl.col('total_funding') > 1_000_000))
reports.write_csv(OUT / 'candidate_report_history.csv')
audit.write_csv(OUT / 'latest_candidate_reports_and_funding.csv')
answer = ('No projects meet all the criteria as of 2022-11-01.' if result.is_empty()
          else '; '.join(f"{candidates[r['project']]} (${r['total_funding']:,.0f})" for r in result.iter_rows(named=True)))
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(audit)
print(answer)
