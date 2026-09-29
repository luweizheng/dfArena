import json
import re
from datetime import date, datetime
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
CUTOFF = date(2023, 1, 1)

def normalize(s):
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

# Entity aliases established from agenda headings and descriptions. Agency
# suffixes identify funding programs, not separate projects.
def canonical(s):
    s = normalize(s)
    s = re.sub(r'_(?:caljpia_fema|fema_caloes|fema|caloes|caljpia)_project$', '', s)
    s = re.sub(r'_fema$', '', s)
    if re.fullmatch(r'(?:20\d\d_)?annual_street_maintenance', s):
        return 'annual_street_maintenance'
    aliases = {
        'guardrail_replacement_citywide': 'citywide_guardrail_replacement',
        'malibu_park_drainage_improvements': 'malibu_park_storm_drain_repairs',
        'storm_drain_trash_screens_phase_two': 'storm_drain_trash_screens',
        'broad_beach_road_water_quality_repair': 'broad_beach_road_water_quality_infrastructure_repairs',
        'clover_heights_storm_drainage_improvements': 'clover_heights_storm_drain',
        'encinal_canyon_road_repairs': 'encinal_canyon_road_drainage_improvements',
        'latigo_canyon_road_retaining_wall_repair_project': 'latigo_canyon_road_roadway_retaining_wall_improvements',
        'malibu_bluffs_park_south_walkway_repairs': 'malibu_bluffs_park_south_walkway',
        'point_dume_walkway_repairs': 'point_dume_decomposed_granite_walkway_repair_project',
        'outdoor_warningn_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_signs': 'outdoor_warning_sirens',
        'trancas_playground_resurfacing': 'trancas_canyon_park_playground',
        'trancas_canyon_park_playground_resurfacing': 'trancas_canyon_park_playground',
        'malibu_bluffs_park_roof_replacement_project': 'michael_landon_center_roof_replacement_project',
    }
    return aliases.get(s, s)

funding = pl.read_parquet(ROOT / 'funding/Funding.parquet')
docs = pl.read_parquet(ROOT / 'civic_docs/civic_docs.parquet')
vocabulary = set(funding['project_name'].to_list()) - {'discussion', 'recommended_action'}
section = re.compile(r'(?:Capital Improvement(?: and Disaster Recovery)?|Disaster(?: Recovery)?) Projects\s*\((Design|Construction|Completed|Not Started)\)', re.I)
records = []
dates = []
for doc in docs.iter_rows(named=True):
    text = doc['report_content']
    raw_date = re.search(r'Meeting date:\s*([^\n]+)', text, re.I)[1].strip()
    try:
        meeting = datetime.strptime(raw_date, '%B %d, %Y').date()
    except ValueError:
        meeting = datetime.strptime(raw_date, '%b %d, %Y').date()
    if doc['report_id'] == 'rid_0010':
        meeting = date(2022, 1, 26)  # Explicit authoritative correction in hints.
    dates.append({'report_id': doc['report_id'], 'header_date': raw_date, 'meeting_date': meeting})
    sections = list(section.finditer(text))
    for i, match in enumerate(sections):
        body = text[match.end():sections[i+1].start() if i+1 < len(sections) else len(text)]
        lines = body.splitlines()
        for j, line in enumerate(lines):
            # Match complete project headings only, never narrative mentions.
            for n in (1, 2):
                heading = ' '.join(lines[j:j+n]).strip()
                key = normalize(heading)
                if key in vocabulary:
                    records.append({'report_id': doc['report_id'], 'meeting_date': meeting,
                                    'heading': heading, 'project': canonical(key),
                                    'status': match[1].lower()})
                    break

reports = pl.DataFrame(records).unique()
reports.write_csv(OUT / 'extracted_statuses.csv')
pl.DataFrame(dates).write_csv(OUT / 'report_dates.csv')
latest = (reports.filter(pl.col('meeting_date') <= CUTOFF)
          .sort('meeting_date').group_by('project').agg(
              pl.col('meeting_date').last(), pl.col('report_id').last(), pl.col('status').last()))
totals = (funding.with_columns(
    pl.col('grant_time').str.to_date('%Y-%m-%d'),
    pl.col('project_name').map_elements(canonical, return_dtype=pl.String).alias('project'))
    .filter(pl.col('grant_time') <= CUTOFF)
    .group_by('project').agg(pl.col('amount').sum().alias('total_usd')))
ranking = (latest.filter(pl.col('status') == 'completed').join(totals, on='project')
           .sort('total_usd', descending=True))
ranking.write_csv(OUT / 'completed_funding_ranking.csv')
latest.write_csv(OUT / 'latest_statuses.csv')
print(ranking)
winner = ranking.row(0, named=True)
name = winner['project'].replace('_', ' ').title()
answer = f"{name}: ${winner['total_usd']:,} USD."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(answer)
