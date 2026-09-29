import json
from datetime import datetime, timezone
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
def clean(column):
    return pl.col(column).str.strip_chars().str.strip_chars_start('#')

cases = pl.read_parquet(DATA / 'support/Case.parquet').with_columns(
    clean('id'), clean('ownerid'), pl.col('status').str.strip_chars(),
    pl.col('createddate').str.to_datetime(time_zone='UTC'),
    pl.col('closeddate').str.to_datetime(time_zone='UTC'),
)
history = pl.read_parquet(DATA / 'support/casehistory__c.parquet').with_columns(
    clean('caseid__c'), clean('newvalue__c'), clean('oldvalue__c'),
    pl.col('field__c').str.strip_chars(),
)
# Rolling four calendar months preceding the supplied current date.
start = datetime(2023, 5, 2, tzinfo=timezone.utc)
end = datetime(2023, 9, 3, tzinfo=timezone.utc)
recent = cases.filter((pl.col('createddate') >= start) & (pl.col('createddate') < end))
assignments = history.filter(pl.col('field__c') == 'Owner Assignment')
assignment_counts = assignments.group_by('caseid__c').agg(pl.len().alias('assignments'))
# Each initial or subsequent assignee receives one count per distinct case;
# open cases and transferred cases remain in this eligibility computation.
handled = assignments.join(recent.select('id'), left_on='caseid__c', right_on='id').select(
    pl.col('caseid__c').alias('id'), pl.col('newvalue__c').alias('agent')
).unique()
eligible = handled.group_by('agent').agg(pl.col('id').n_unique().alias('case_count')).filter(pl.col('case_count') > 1)
closed = recent.join(assignment_counts, left_on='id', right_on='caseid__c').filter(
    (pl.col('assignments') == 1) & (pl.col('status') == 'Closed') &
    pl.col('closeddate').is_not_null() & (pl.col('closeddate') < end)
).with_columns((pl.col('closeddate') - pl.col('createddate')).dt.total_seconds().alias('handle_seconds'))
ranking = closed.group_by('ownerid').agg(pl.col('handle_seconds').mean().alias('average_handle_seconds')).join(
    eligible, left_on='ownerid', right_on='agent'
).sort(['average_handle_seconds', 'ownerid'])
assert ranking.height > 0
ranking.write_csv(OUT / 'agent_handle_times.csv')
answer = ranking.item(0, 'ownerid')
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(ranking)
print(answer)
