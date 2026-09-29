import json
from datetime import datetime, timezone
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def clean(column):
    return pl.col(column).str.strip_chars().str.strip_prefix('#')

# Four completed calendar quarters before the task's date (2023-04-10).
today = datetime(2023, 4, 10, tzinfo=timezone.utc)
end = datetime(today.year, 3 * ((today.month - 1) // 3) + 1, 1, tzinfo=timezone.utc)
start = end.replace(year=end.year - 1)
users = pl.read_parquet(DATA / 'core_crm/User.parquet').select(clean('Id').alias('agent')).unique()
cases = pl.read_parquet(DATA / 'support/Case.parquet').select(clean('id').alias('caseid__c')).unique()
history = (
    pl.read_parquet(DATA / 'support/casehistory__c.parquet')
    .with_columns([clean(c).alias(c) for c in ['caseid__c', 'oldvalue__c', 'newvalue__c']])
    .filter(pl.col('field__c').str.strip_chars() == 'Owner Assignment')
    .with_columns(pl.col('createddate').str.to_datetime(time_zone='UTC').alias('timestamp'))
    .join(cases, on='caseid__c', how='semi')
)
period = history.filter((pl.col('timestamp') >= start) & (pl.col('timestamp') < end))
# Both initial recipients and subsequent owners handled the case. Outgoing
# owners also necessarily handled their transferred case during this period.
handled = (
    pl.concat([
        period.select('caseid__c', pl.col('newvalue__c').alias('agent')),
        period.select('caseid__c', pl.col('oldvalue__c').alias('agent')),
    ])
    .join(users, on='agent', how='semi')
    .group_by('agent').agg(pl.col('caseid__c').n_unique().alias('cases_handled'))
)
transfers = (
    period.filter(pl.col('oldvalue__c').is_not_null() & (pl.col('oldvalue__c') != pl.col('newvalue__c')))
    .join(users, left_on='newvalue__c', right_on='agent', how='semi')
    .select(pl.col('oldvalue__c').alias('agent'))
    .join(users, on='agent', how='semi')
    .group_by('agent').len(name='transfer_count')
)
ranking = transfers.join(handled, on='agent').filter(pl.col('cases_handled') > 0).sort(['transfer_count', 'agent'])
assert ranking.height > 0, 'No eligible agent'
winners = ranking.filter(pl.col('transfer_count') == ranking['transfer_count'].min())
assert winners.height == 1, 'Minimum is tied'
answer = winners['agent'][0]
ranking.write_csv(OUT / 'transfer_counts.csv')
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(ranking)
print(answer)

if __name__ == '__main__':
    pass
