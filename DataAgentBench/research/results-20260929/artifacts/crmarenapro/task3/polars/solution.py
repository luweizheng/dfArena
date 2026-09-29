import json
import re
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
query = json.loads(Path('/workspace/task.json').read_text())['query']
opportunity_id = re.search(r'Opportunity Id to be considered is:\s*(\w+)', query).group(1)
def clean_id(col):
    return pl.col(col).str.strip_chars().str.strip_chars_start('#')

opportunity = pl.scan_parquet(ROOT / 'sales_pipeline/Opportunity.parquet').filter(clean_id('Id') == opportunity_id).collect()
assert opportunity.height == 1
tasks = pl.scan_parquet(ROOT / 'activities/Task.parquet').filter(clean_id('WhatId') == opportunity_id).with_columns(pl.concat_str([pl.col('Subject').fill_null(''), pl.col('Description').fill_null('')], separator=' ').str.to_lowercase().alias('text')).collect()
assert tasks.height > 0
# Identify the furthest sales milestone evidenced by the opportunity's tasks.
# Preparing an unsigned contract and agreeing terms are negotiation, not closure.
stage_patterns = [
    ('Qualification', r'qualif|budget|decision.maker|initial contact'),
    ('Discovery', r'discover|requirements|needs|product demo|case studies'),
    ('Quote', r'proposal|quote|quotation'),
    ('Negotiation', r'negotiat|finalize pricing|contract for (approval|review)|final contract'),
    ('Closed', r'contract (?:is |has been )?signed|deal (?:is )?closed|closed won|closed lost|handoff to implementation'),
]
evidence = {stage: tasks.filter(pl.col('text').str.contains(pattern)).height for stage, pattern in stage_patterns}
matched = [stage for stage, _ in stage_patterns if evidence[stage]]
assert matched, 'No recognizable sales-stage evidence'
answer = matched[-1]
Path('/workspace/work/evidence.json').write_text(json.dumps({'current_stage': opportunity['StageName'][0], 'stage_task_counts': evidence, 'tasks': tasks.to_dicts()}, indent=2))
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
print(answer)
