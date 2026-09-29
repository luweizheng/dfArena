import re
import json
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
START, END = date(2021, 6, 1), date(2023, 1, 1)
docs = pl.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
funding = pl.read_parquet('/workspace/data/funding/Funding.parquet')

def normalize(s):
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

# Entity aliases established from agenda headings and descriptions. Agency
# parentheticals identify funding programs, not different civic projects.
def canonical(s):
    s = normalize(s)
    s = re.sub(r'_(?:caljpia_fema|fema_caloes|caljpia|caloes|fema)_project$', '', s)
    s = re.sub(r'^20\d\d_(?=annual_street_maintenance)', '', s)
    aliases = {
        'guardrail_replacement_citywide': 'citywide_guardrail_replacement',
        'malibu_park_storm_drain_repairs': 'malibu_park_drainage_improvements',
        'broad_beach_road_water_quality_repair': 'broad_beach_road_water_quality_infrastructure_repairs',
        'clover_heights_storm_drainage_improvements': 'clover_heights_storm_drain',
        'encinal_canyon_road_repairs': 'encinal_canyon_road_drainage_improvements',
        'latigo_canyon_road_retaining_wall_repair_project': 'latigo_canyon_road_roadway_retaining_wall_improvements',
        'westward_beach_road_repair_project': 'westward_beach_road_improvements_project',
        'westward_beach_road_drainage_improvements_project': 'westward_beach_road_shoulder_repairs',
        'malibu_bluffs_park_south_walkway_repairs': 'malibu_bluffs_park_south_walkway',
        'trancas_playground_resurfacing': 'trancas_canyon_park_playground',
        'trancas_canyon_park_playground_resurfacing': 'trancas_canyon_park_playground',
        'trancas_canyon_park_upper_and_lower_slopes_repair': 'trancas_canyon_park_slope_stabilization_project',
        'point_dume_walkway_repairs': 'point_dume_decomposed_granite_walkway_repair_project',
        'malibu_bluffs_park_roof_replacement_project': 'michael_landon_center_roof_replacement_project',
        'storm_drain_trash_screens_phase_two': 'storm_drain_trash_screens',
        'outdoor_warningn_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_fema': 'outdoor_warning_sirens',
        'outdoor_warning_signs': 'outdoor_warning_sirens',
    }
    return aliases.get(s, s)

names = set(funding['project_name'].to_list()) - {'discussion', 'recommended_action'}
section_re = re.compile(r'^(?:Capital Improvement(?: and Disaster Recovery)?|Disaster(?: Recovery)?) Projects?\s*\((Design|Construction|Completed|Not Started)\)', re.I)
records = []
report_dates = []
for row in docs.iter_rows(named=True):
    text = row['report_content']
    raw_date = re.search(r'Meeting date:\s*([^\n]+)', text, re.I).group(1).strip()
    for fmt in ('%B %d, %Y', '%b %d, %Y'):
        try:
            meeting_date = datetime.strptime(raw_date, fmt).date()
            break
        except ValueError:
            pass
    if row['report_id'] == 'rid_0010':
        meeting_date = date(2022, 1, 26)  # Explicit task correction.
    report_dates.append({'report_id': row['report_id'], 'date': meeting_date})
    if not START <= meeting_date <= END:
        continue
    status = None
    for line in text.splitlines():
        line = line.strip()
        match = section_re.match(line)
        if match:
            status = match.group(1).lower()
        elif status and normalize(line) in names:
            records.append({'report_id': row['report_id'], 'date': meeting_date,
                            'heading': line, 'project': canonical(line), 'status': status})
observations = pl.DataFrame(records).unique()
# Different statuses must be witnessed in different reports, not just twice
# within the same report. Retain all section assignments where duplicated.
a = observations.select('project', 'report_id', 'status').unique()
changed = (a.join(a, on='project', suffix='_other')
    .filter((pl.col('report_id') != pl.col('report_id_other')) &
            (pl.col('status') != pl.col('status_other')))
    .select('project').unique())
funding_clean = funding.with_columns(
    pl.col('grant_time').str.to_date('%Y-%m-%d').alias('date'),
    pl.col('project_name').map_elements(canonical, return_dtype=pl.String).alias('project'))
totals = (funding_clean.filter(pl.col('date').is_between(START, END, closed='both'))
          .group_by('project').agg(pl.col('amount').sum().alias('total_funding')))
result = changed.join(totals, on='project', how='left').with_columns(pl.col('total_funding').fill_null(0)).sort('project')
average = (Decimal(result['total_funding'].sum()) / Decimal(result.height)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
observations.sort('date', 'project').write_csv(OUT / 'status_observations.csv')
pl.DataFrame(report_dates).write_csv(OUT / 'report_dates.csv')
result.write_csv(OUT / 'project_funding_totals.csv')
(OUT / 'answer.json').write_text(json.dumps({'answer': f'${average:,.2f} USD'}))
print(result)
print(f'Projects: {result.height}; total funding: {result["total_funding"].sum()}; average: {average}')
