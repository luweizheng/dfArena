import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
request = json.loads(Path('/workspace/task.json').read_text())
opportunity_id = re.search(r'006[A-Za-z0-9]+', request['query']).group()

def clean_id(series):
    return series.astype('string').str.strip().str.lstrip('#')

opportunities = pd.read_parquet(ROOT / 'sales_pipeline/Opportunity.parquet')
tasks = pd.read_parquet(ROOT / 'activities/Task.parquet')
opportunity = opportunities.loc[clean_id(opportunities['Id']).eq(opportunity_id)]
assert len(opportunity) == 1
related = tasks.loc[clean_id(tasks['WhatId']).eq(opportunity_id)].copy()
assert not related.empty
text = related['Subject'].fillna('').str.strip() + ' ' + related['Description'].fillna('').str.strip()
# Tasks may span earlier phases. The most advanced explicit sales activity
# establishes the represented stage; preparing a signature is not a closed deal.
patterns = {
    'Qualification': r'qualif|lead scoring|initial outreach',
    'Discovery': r'discovery|requirements|needs assessment|product demo|case studies',
    'Quote': r'proposal|quote|quotation',
    'Negotiation': r'negotiat|finalize pricing|final contract|contract for approval',
    'Closed': r'contract (?:has been |is )?signed|deal (?:is )?closed|closed won|closed lost|handoff to implementation',
}
matches = {stage: text.str.contains(pattern, case=False, regex=True).sum().item()
           for stage, pattern in patterns.items()}
represented = [stage for stage in patterns if matches[stage] > 0]
assert represented, 'No stage evidence found'
answer = represented[-1]
related.to_json(OUT / 'task_evidence.json', orient='records', indent=2)
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps({'current_stage': opportunity.iloc[0]['StageName'], 'stage_evidence': matches, 'answer': answer}))
