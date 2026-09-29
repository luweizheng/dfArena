import json
from datetime import datetime, timezone
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
today = datetime(2022, 10, 26, tzinfo=timezone.utc)
# LAST_N_QUARTERS: the six complete calendar quarters preceding this quarter.
quarter_month = ((today.month - 1) // 3) * 3 + 1
end = datetime(today.year, quarter_month, 1, tzinfo=timezone.utc)
month_index = end.year * 12 + end.month - 1 - 6 * 3
start = datetime(month_index // 12, month_index % 12 + 1, 1, tzinfo=timezone.utc)

def clean_id(name):
    return pl.col(name).str.strip_chars().str.strip_chars_start('#')

accounts = pl.read_parquet(DATA / 'core_crm/Account.parquet').select(
    clean_id('Id').alias('accountid'),
    pl.col('ShippingState').str.strip_chars().alias('state'),
)
cases = pl.read_parquet(DATA / 'support/Case.parquet').with_columns(
    clean_id('accountid'),
    pl.col('status').str.strip_chars(),
    pl.col('createddate').str.strip_chars().str.to_datetime('%Y-%m-%dT%H:%M:%S%.f%z'),
    pl.col('closeddate').str.strip_chars().str.to_datetime('%Y-%m-%dT%H:%M:%S%.f%z'),
)
ranked = (
    cases.filter(
        (pl.col('status') == 'Closed')
        & (pl.col('closeddate') >= start)
        & (pl.col('closeddate') < end)
    )
    .join(accounts, on='accountid', how='inner', validate='m:1')
    .filter(pl.col('state').is_not_null() & (pl.col('state') != ''))
    .with_columns((pl.col('closeddate') - pl.col('createddate')).dt.total_seconds().alias('closure_seconds'))
    .group_by('state')
    .agg(pl.col('closure_seconds').mean().alias('mean_closure_seconds'), pl.len().alias('case_count'))
    .sort(['mean_closure_seconds', 'state'])
)
ranked.write_csv(OUT / 'state_closure_times.csv')
answer = ranked.item(0, 'state')
assert len(answer) == 2
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(ranked)
