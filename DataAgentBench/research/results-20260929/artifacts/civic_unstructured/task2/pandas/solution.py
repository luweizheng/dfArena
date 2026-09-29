import json
import re
from pathlib import Path
import pandas as pd

OUT = Path('/workspace/work')
CUTOFF = pd.Timestamp('2023-01-01')
docs = pd.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
funding = pd.read_parquet('/workspace/data/funding/Funding.parquet')

def normalize(value):
    value = re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')
    value = re.sub(r'_(?:fema_caloes|caljpia_fema|caljpia|caloes|fema)(?:_project)?$', '', value)
    value = re.sub(r'^20\d\d_annual_street_maintenance$', 'annual_street_maintenance', value)
    aliases = {
        'citywide_guardrail_replacement': 'guardrail_replacement_citywide',
        'storm_drain_trash_screens_phase_two': 'storm_drain_trash_screens',
        'malibu_park_storm_drain_repairs': 'malibu_park_drainage_improvements',
        'outdoor_warningn_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_design': 'outdoor_warning_sirens',
        'trancas_playground_resurfacing': 'trancas_canyon_park_playground_resurfacing',
        'trancas_canyon_park_playground': 'trancas_canyon_park_playground_resurfacing',
        'westward_beach_road_repair_project': 'westward_beach_road_improvements_project',
        'point_dume_walkway_repairs': 'point_dume_decomposed_granite_walkway_repair_project',
        'malibu_bluffs_park_south_walkway_repairs': 'malibu_bluffs_park_south_walkway',
        'broad_beach_road_water_quality_repair': 'broad_beach_road_water_quality_infrastructure_repairs',
        'clover_heights_storm_drainage_improvements': 'clover_heights_storm_drain',
        'latigo_canyon_road_retaining_wall_repair_project': 'latigo_canyon_road_roadway_retaining_wall_improvements',
        'malibu_bluffs_park_roof_replacement_project': 'michael_landon_center_roof_replacement_project',
    }
    return aliases.get(value, value)

funding['project'] = funding.project_name.map(normalize)
known = set(funding.project) - {'recommended_action', 'discussion'}
section = re.compile(r'(?:Capital Improvement(?: and Disaster Recovery)?|Disaster) Projects \((Design|Construction|Completed|Not Started)\)', re.I)
records = []
for row in docs.itertuples():
    text = row.report_content
    date = pd.to_datetime(re.search(r'Meeting date:\s*([^\n]+)', text, re.I).group(1))
    # Binding correction from context/hints.md; report text discusses January 2022.
    if row.report_id == 'rid_0010':
        date = pd.Timestamp('2022-01-26')
    if date > CUTOFF:
        continue
    status = None
    for position, line in enumerate(text.splitlines()):
        match = section.search(line)
        if match:
            status = match.group(1).lower()
            line = line[match.end():].strip()
        name = normalize(line)
        if status and name in known:
            records.append(dict(project=name, report_id=row.report_id, date=date,
                                status=status, position=position, title=line.strip()))
reports = pd.DataFrame(records).sort_values(['date', 'position'])
latest = reports.drop_duplicates('project', keep='last')
funding['date'] = pd.to_datetime(funding.grant_time)
totals = funding.loc[funding.date.le(CUTOFF)].groupby('project').amount.sum()
ranked = latest.loc[latest.status.eq('completed')].merge(totals.rename('funding_usd'), on='project').sort_values('funding_usd', ascending=False)
reports.to_csv(OUT / 'extracted_reports.csv', index=False)
latest.to_csv(OUT / 'latest_status.csv', index=False)
ranked.to_csv(OUT / 'completed_funding.csv', index=False)
winner = ranked.iloc[0]
answer = f"{winner['title']} — ${int(winner.funding_usd):,} USD."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(ranked[['project','date','funding_usd']].to_string(index=False))
print(answer)
