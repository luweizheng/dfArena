import json
from pathlib import Path
import ibis

con = ibis.duckdb.connect()
cases = con.read_parquet('/workspace/data/support/Case.parquet')
accounts = con.read_parquet('/workspace/data/core_crm/Account.parquet')

def clean_id(col):
    return col.strip().re_replace(r'^#+', '')

cases = cases.select(
    case_id=clean_id(cases.id),
    account_id=clean_id(cases.accountid),
    status=cases.status.strip(),
    created=cases.createddate.cast('timestamp'),
    closed=cases.closeddate.cast('timestamp'),
)
accounts = accounts.select(account_key=clean_id(accounts.Id), state=accounts.ShippingState.strip())
# The previous six complete calendar quarters: 2021 Q2 through 2022 Q3.
as_of = ibis.timestamp('2022-10-26')
end = as_of.truncate('Q')
start = end - ibis.interval(months=18)
closed = cases.filter(
    cases.status == 'Closed',
    cases.closed.notnull(),
    cases.closed >= start,
    cases.closed < end,
    cases.created.notnull(),
)
joined = closed.join(accounts, closed.account_id == accounts.account_key)
joined = joined.filter(joined.state.notnull(), joined.state != '')
joined = joined.mutate(closure_seconds=joined.closed.epoch_seconds() - joined.created.epoch_seconds())
ranking = joined.group_by('state').aggregate(
    mean_closure_seconds=joined.closure_seconds.mean(),
    case_count=joined.count(),
).order_by('mean_closure_seconds', 'state')
rows = ranking.to_pyarrow().to_pylist()
assert rows, 'No qualifying cases'
Path('/workspace/work/state_ranking.json').write_text(json.dumps(rows, indent=2))
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': rows[0]['state']}))
print(json.dumps(rows[:5], indent=2))
