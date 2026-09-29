import json
import re
from pathlib import Path
import pandas as pd

OUT = Path('/workspace/work')
CUTOFF = pd.Timestamp('2022-06-01')
docs = pd.read_parquet('/workspace/data/civic_docs/civic_docs.parquet')
funding = pd.read_parquet('/workspace/data/funding/Funding.parquet')

def slug(name):
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

def canonical(name):
    name = slug(name)
    name = re.sub(r'_(?:fema_caloes|caljpia_fema|fema|caloes|caljpia)(?:_project)?$', '', name)
    name = re.sub(r'^20\d\d_(?=annual_street_maintenance)', '', name)
    aliases = {
        'storm_drain_trash_screens_phase_two': 'storm_drain_trash_screens',
        'malibu_park_storm_drain_repairs': 'malibu_park_drainage_improvements',
        'guardrail_replacement_citywide': 'citywide_guardrail_replacement',
        'outdoor_warningn_sirens_design': 'outdoor_warning_sirens',
        'outdoor_warning_sirens_design': 'outdoor_warning_sirens',
        'broad_beach_road_water_quality_repair': 'broad_beach_road_water_quality_infrastructure_repairs',
        'trancas_playground_resurfacing': 'trancas_canyon_park_playground_resurfacing',
        'trancas_canyon_park_playground': 'trancas_canyon_park_playground_resurfacing',
        'clover_heights_storm_drainage_improvements': 'clover_heights_storm_drain',
        'malibu_bluffs_park_south_walkway_repairs': 'malibu_bluffs_park_south_walkway',
    }
    return aliases.get(name, name)

known = set(funding.project_name) - {'discussion', 'recommended_action'}
section_pattern = re.compile(r'(Capital Improvement|Disaster) Projects\s*\((Design|Construction|Completed|Not Started)\)', re.I)
rows = []
for report in docs.itertuples():
    date = pd.to_datetime(re.search(r'Meeting date:\s*([^\n]+)', report.report_content)[1])
    # Explicit date correction from context/hints.md, consistent with January updates.
    if report.report_id == 'rid_0010':
        date = pd.Timestamp('2022-01-26')
    if date > CUTOFF:
        continue
    sections = list(section_pattern.finditer(report.report_content))
    for j, section in enumerate(sections):
        end = sections[j + 1].start() if j + 1 < len(sections) else len(report.report_content)
        body = report.report_content[section.end():end]
        body = re.sub(r'Page \d+ of \d+\s*Agenda Item # [^\n]+', '', body)
        lines = body.splitlines()
        # Titles can wrap across lines. Exact matches to funding names avoid prose
        # and noise records; punctuation is normalized, but separate headings stay separate.
        for i in range(len(lines)):
            for width in range(1, 4):
                title = ' '.join(lines[i:i+width]).strip()
                if not lines[i].strip() or not lines[min(i+width-1,len(lines)-1)].strip():
                    continue
                key = slug(title)
                if key in known:
                    rows.append(dict(project=canonical(key), title=title,
                        date=date, report_id=report.report_id,
                        type='capital' if section[1].lower().startswith('capital') else 'disaster',
                        status=section[2].lower()))

reports = pd.DataFrame(rows).drop_duplicates()
latest = reports.sort_values('date', kind='stable').drop_duplicates('project', keep='last')
candidates = latest.loc[(latest.type == 'capital') & (latest.status == 'construction')].copy()
funding['date'] = pd.to_datetime(funding.grant_time)
funding['project'] = funding.project_name.map(canonical)
totals = funding.loc[funding.date <= CUTOFF].groupby('project').amount.sum()
candidates['total_funding'] = candidates.project.map(totals).fillna(0).astype('int64')
candidates = candidates.sort_values(['total_funding', 'project'])
assert len(candidates) > 0
winner = candidates.iloc[0]
answer = f"{winner['title']}: ${winner['total_funding']:,.0f} USD."
reports.to_csv(OUT / 'extracted_reports.csv', index=False)
candidates.to_csv(OUT / 'eligible_projects.csv', index=False)
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(candidates[['title','date','report_id','total_funding']].to_string(index=False))
print(answer)
