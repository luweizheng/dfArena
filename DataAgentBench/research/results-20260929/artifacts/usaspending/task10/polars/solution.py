import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
contracts = pl.read_parquet(DATA / 'contracts_db/contracts.parquet')
amounts = pl.read_parquet(DATA / 'contracts_db/contract_amounts.parquet').with_row_index('original_row')
recipients = pl.read_parquet(DATA / 'recipients_db/recipients.parquet')

# Actual identifiers match directly; do not normalize or merge distinct UEIs.
assert contracts['award_id'].n_unique() == contracts.height
assert amounts.join(contracts, on='award_id', how='anti').is_empty()
assert contracts.join(recipients, left_on='recipient_uei', right_on='uei', how='anti').is_empty()
counts = contracts.group_by('recipient_uei').agg(pl.len().alias('contract_count'))
ranked = counts.join(recipients, left_on='recipient_uei', right_on='uei').sort(
    ['contract_count', 'recipient_uei'], descending=[True, False]
)
assert ranked.filter(pl.col('contract_count') != pl.col('n_contracts')).is_empty()
assert ranked['contract_count'][9] > ranked['contract_count'][10]
top = ranked.head(10)

# The first original record is authoritative; subsequent entries are superseded.
first_rows = amounts.group_by('award_id').agg(pl.col('original_row').min().alias('first_row'))
superseded_awards = (
    amounts.join(first_rows, on='award_id')
    .filter(pl.col('original_row') > pl.col('first_row'))
    .select('award_id').unique()
)
matched = contracts.join(top.select('recipient_uei'), on='recipient_uei', how='semi').join(
    superseded_awards, on='award_id', how='semi'
)
result = matched.height
by_recipient = matched.group_by('recipient_uei').agg(pl.len().alias('contracts_with_superseded_amount'))
top.join(by_recipient, on='recipient_uei', how='left').write_csv(OUT / 'recipient_counts.csv')
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{result} contracts.'}) + '\n')
print(json.dumps({'answer': f'{result} contracts.'}))

if __name__ == '__main__':
    pass
