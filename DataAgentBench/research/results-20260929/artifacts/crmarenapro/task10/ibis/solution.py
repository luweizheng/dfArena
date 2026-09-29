import json
from pathlib import Path
import ibis

con = ibis.duckdb.connect()
def clean(expr):
    return expr.strip().re_replace(r'^#+', '')

raw = con.read_parquet('/workspace/data/support/Case.parquet')
cases = raw.select(case_id=clean(raw.id), agent_id=clean(raw.ownerid),
                   opened=raw.createddate.cast('timestamp'),
                   closed=raw.closeddate.cast('timestamp'))
h = con.read_parquet('/workspace/data/support/casehistory__c.parquet')
assignments = h.filter(h.field__c.strip() == 'Owner Assignment').select(
    case_id=clean(h.caseid__c), agent_id=clean(h.newvalue__c))
# Rolling four calendar months ending on the supplied date.
today = ibis.timestamp('2023-09-02 00:00:00')
start = today - ibis.interval(months=4)
end = today + ibis.interval(days=1)
recent = cases.filter((cases.opened >= start) & (cases.opened < end))
# All agents assigned to each case qualify for the volume count, including
# transferred and still-open cases. Current owners also cover missing history.
involved = assignments.join(recent.select('case_id'), 'case_id').select('case_id', 'agent_id')
involved = involved.union(recent.select('case_id', 'agent_id'), distinct=True)
counts = involved.group_by('agent_id').aggregate(case_count=involved.case_id.nunique())
eligible = counts.filter(counts.case_count > 1)
assignment_counts = assignments.group_by('case_id').aggregate(assignment_count=assignments.count())
closed = recent.join(assignment_counts, 'case_id').filter(
    ibis._.assignment_count == 1,
    ibis._.closed.notnull(),
    ibis._.closed < end,
)
closed = closed.mutate(handle_seconds=closed.closed.epoch_seconds() - closed.opened.epoch_seconds())
averages = closed.group_by('agent_id').aggregate(average_handle_seconds=closed.handle_seconds.mean())
ranking = averages.join(eligible, 'agent_id').order_by('average_handle_seconds', 'agent_id')
rows = ranking.to_pyarrow().to_pylist()
if not rows:
    raise ValueError('No eligible agents with non-transferred closed cases')
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': rows[0]['agent_id']}))
print(json.dumps(rows, indent=2))
