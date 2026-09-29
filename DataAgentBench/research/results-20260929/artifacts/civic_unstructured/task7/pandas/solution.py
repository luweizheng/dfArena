import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
CUTOFF = pd.Timestamp('2022-11-01')

def canonical(name):
    name = re.sub(r'[^a-z0-9]+', ' ', name.lower()).strip()
    name = re.sub(r' (?:fema|caloes|caljpia)(?: (?:fema|caloes|caljpia))*(?: project)?$', '', name)
    name = re.sub(r'^20\d\d annual street', 'annual street', name)
    name = name.replace('storm drain trash screens phase two', 'storm drain trash screens')
    name = name.replace('outdoor warningn sirens', 'outdoor warning sirens')
    name = re.sub(r'^(outdoor warning sirens) design$', r'\1', name)
    aliases = {
        'clover heights storm drainage improvements': 'clover heights storm drain',
        'encinal canyon 60 inch storm drain repairs': 'encinal canyon road drainage improvements',
        'broad beach road water quality repair': 'broad beach road water quality infrastructure repairs',
        'latigo canyon road retaining wall repair project': 'latigo canyon road roadway retaining wall improvements',
        'citywide guardrail replacement': 'guardrail replacement citywide',
        'trancas canyon park upper and lower slopes repair': 'trancas canyon park slope stabilization project',
        'trancas playground resurfacing': 'trancas canyon park playground resurfacing',
        'trancas canyon park playground': 'trancas canyon park playground resurfacing',
        'point dume walkway repairs': 'point dume decomposed granite walkway repair project',
        'malibu bluffs park south walkway repairs': 'malibu bluffs park south walkway',
        'westward beach road repair project': 'westward beach road improvements project',
    }
    return aliases.get(name, name)

funding = pd.read_parquet(DATA / 'funding/Funding.parquet')
funding['project'] = funding.project_name.map(canonical)
funding['date'] = pd.to_datetime(funding.grant_time)
known = set(funding.project) - {'discussion', 'recommended action'}
docs = pd.read_parquet(DATA / 'civic_docs/civic_docs.parquet')
section = re.compile(r'^(Capital Improvement|Disaster) Projects\s*\((Design|Construction|Completed|Not Started)\)$', re.I)
rows = []
dates = []
for doc in docs.itertuples():
    stated = re.search(r'Meeting date:\s*([^\n]+)', doc.report_content).group(1)
    date = pd.Timestamp('2022-01-26') if doc.report_id == 'rid_0010' else pd.Timestamp(stated)
    dates.append({'report_id': doc.report_id, 'stated_date': stated, 'effective_date': date})
    if date > CUTOFF:
        continue
    kind = status = None
    for line in doc.report_content.splitlines():
        line = line.strip()
        heading = section.fullmatch(line)
        if heading:
            kind = 'disaster' if heading[1].lower() == 'disaster' else 'capital'
            status = heading[2].lower()
        elif kind and canonical(line) in known:
            rows.append(dict(report_id=doc.report_id, date=date, project=canonical(line),
                             title=line, type=kind, status=status))
reports = pd.DataFrame(rows).drop_duplicates()
# Every disaster/not-started project heading in the source is one line and
# matches a funding identity. Verify extraction of those sections explicitly.
for doc in docs.itertuples():
    for block in re.findall(r'Disaster Projects \(Not Started\)(.*?)(?=(?:Capital Improvement|Disaster) Projects \(|\Z)', doc.report_content, re.S):
        clean = re.sub(r'Page \d+ of \d+|Agenda Item # [^\n]+', '', block)
        for title in re.findall(r'(?:^|\n)\s*([^\n]+)\s*\n\s*\(cid:190\) Project Description:', clean):
            assert canonical(title) in known, title
latest = reports.sort_values('date').groupby('project', as_index=False).tail(1)
totals = funding.loc[funding.date <= CUTOFF].groupby('project').amount.sum().rename('total_funding')
latest = latest.join(totals, on='project')
result = latest.loc[(latest.type == 'disaster') & (latest.status == 'not started') & (latest.total_funding > 1_000_000)].sort_values('project')
reports.to_csv(OUT / 'extracted_reports.csv', index=False)
latest.to_csv(OUT / 'latest_reports_and_funding.csv', index=False)
pd.DataFrame(dates).to_csv(OUT / 'report_dates.csv', index=False)
answer = ('No projects meet all the criteria as of 2022-11-01.' if result.empty else '; '.join(f"{r.title} (${r.total_funding:,.0f})" for r in result.itertuples()))
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(latest.loc[latest.type == 'disaster', ['project','date','status','total_funding']].to_string(index=False))
print(answer)
