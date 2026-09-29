import json
import re
from datetime import datetime, date
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
CUTOFF = date(2022, 6, 1)

def normalize(name):
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

def canonical(name):
    name = normalize(name)
    name = re.sub(r'_(?:caljpia_fema|fema_caloes|caljpia|fema|caloes)_project$', '', name)
    name = re.sub(r'^20\d\d_annual_street_maintenance$', 'annual_street_maintenance', name)
    aliases = {
        'storm_drain_trash_screens_phase_two': 'storm_drain_trash_screens',
        'malibu_park_drainage_improvements': 'malibu_park_storm_drain_repairs',
        'guardrail_replacement_citywide': 'citywide_guardrail_replacement',
        'outdoor_warningn_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_fema': 'outdoor_warning_sirens',
    }
    return aliases.get(name, name)

docs = pl.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
funding = pl.read_parquet('/workspace/data/funding/Funding.parquet')
known = set(funding['project_name'].to_list()) - {'discussion', 'recommended_action'}
section_re = re.compile(r'^(Capital Improvement|Disaster) Projects \((Design|Construction|Completed|Not Started)\)$')
records = []
for row in docs.iter_rows(named=True):
    content = row['report_content']
    date_text = re.search(r'Meeting date:\s*([^\n]+)', content).group(1).strip()
    try:
        meeting = datetime.strptime(date_text, '%B %d, %Y').date()
    except ValueError:
        meeting = datetime.strptime(date_text, '%b %d, %Y').date()
    # Explicit correction mandated by the supplied hints; internal updates also
    # reference January 2022 despite the copied October 2021 header.
    if row['report_id'] == 'rid_0010':
        meeting = date(2022, 1, 26)
    if meeting > CUTOFF:
        continue
    kind = status = None
    lines = content.splitlines()
    for i, line in enumerate(lines):
        match = section_re.fullmatch(line.strip())
        if match:
            kind = 'capital' if match[1] == 'Capital Improvement' else 'disaster'
            status = match[2].lower()
            continue
        if not kind or not line.strip():
            continue
        # Project titles are matched as complete lines, including wrapped titles;
        # narrative mentions cannot create status observations.
        for width in range(1, 4):
            title = ' '.join(s.strip() for s in lines[i:i+width])
            key = normalize(title)
            if key in known:
                records.append(dict(project=canonical(key), title=title,
                                    report_id=row['report_id'], report_date=meeting,
                                    type=kind, status=status))
                break
observations = pl.DataFrame(records).unique()
observations.write_csv(OUT / 'project_observations.csv')
latest = observations.sort('report_date').group_by('project').last()
eligible = latest.filter((pl.col('type') == 'capital') & (pl.col('status') == 'construction'))
totals = (funding.with_columns(
    pl.col('project_name').map_elements(canonical, return_dtype=pl.String).alias('project'),
    pl.col('grant_time').str.to_date().alias('grant_date'))
    .filter(pl.col('grant_date') <= CUTOFF)
    .group_by('project').agg(pl.col('amount').sum().alias('total_usd')))
ranked = eligible.join(totals, on='project', how='left').with_columns(pl.col('total_usd').fill_null(0)).sort('total_usd')
ranked.write_csv(OUT / 'eligible_project_totals.csv')
assert ranked.height > 0
winner = ranked.row(0, named=True)
answer = f"{winner['title']}: ${winner['total_usd']:,} USD."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(ranked.select('title', 'report_date', 'total_usd'))
print(answer)
