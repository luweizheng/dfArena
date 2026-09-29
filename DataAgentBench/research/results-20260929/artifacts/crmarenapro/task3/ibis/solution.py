import json
import re
from pathlib import Path
import ibis

ROOT = Path('/workspace')
query = json.loads((ROOT / 'task.json').read_text())['query']
opportunity_id = re.search(r'006[A-Za-z0-9]{15}', query).group()
con = ibis.duckdb.connect()
normalize = lambda col: col.strip().re_replace(r'^#', '')
opps = con.read_parquet(str(ROOT / 'data/sales_pipeline/Opportunity.parquet'))
tasks = con.read_parquet(str(ROOT / 'data/activities/Task.parquet'))
opp = opps.filter(normalize(opps.Id) == opportunity_id)
related = tasks.filter(normalize(tasks.WhatId) == opportunity_id)
text = related.Subject.fill_null('').strip().lower() + ' ' + related.Description.fill_null('').strip().lower()
# Classify the sales activities by their substantive milestones. Drafting a
# contract for signature is negotiation; only executed deals indicate closure.
stage = ibis.cases(
    (text.re_search(r'closed won|closed lost|contract (?:is )?signed|executed contract'), 'Closed'),
    (text.re_search(r'negotiat|finalize pricing|contract for (?:approval|review)|final contract'), 'Negotiation'),
    (text.re_search(r'proposal|quot(?:e|ation)|pricing'), 'Quote'),
    (text.re_search(r'demo|case studies|requirements|needs assessment'), 'Discovery'),
    else_='Qualification',
)
classified = related.mutate(inferred_stage=stage, activity_date=related.ActivityDate.cast('date'))
rank = ibis.cases(
    (classified.inferred_stage == 'Closed', 5),
    (classified.inferred_stage == 'Negotiation', 4),
    (classified.inferred_stage == 'Quote', 3),
    (classified.inferred_stage == 'Discovery', 2),
    else_=1,
)
classified = classified.mutate(stage_rank=rank)
result = classified.order_by(ibis.desc('stage_rank'), ibis.desc('activity_date')).to_pyarrow().to_pylist()
assert result, 'No related tasks found'
evidence = {'opportunity': opp.to_pyarrow().to_pylist(), 'tasks': result}
(ROOT / 'work/evidence.json').write_text(json.dumps(evidence, default=str, indent=2))
answer = {'answer': result[0]['inferred_stage']}
(ROOT / 'work/answer.json').write_text(json.dumps(answer))
print(json.dumps(answer))
