import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
contracts = pd.read_parquet(DATA / 'contracts_db/contracts.parquet')
amounts = pd.read_parquet(DATA / 'contracts_db/contract_amounts.parquet')
recipients = pd.read_parquet(DATA / 'recipients_db/recipients.parquet')

# Actual identifiers match directly across these tables.
assert contracts['recipient_uei'].isin(recipients['uei']).all()
assert amounts['award_id'].isin(contracts['award_id']).all()
assert contracts['award_id'].is_unique
assert recipients['uei'].is_unique
counts = contracts.groupby('recipient_uei').size().rename('contract_count')
registered = recipients.set_index('uei')['n_contracts'].reindex(counts.index)
assert counts.eq(registered).all()
ranked = counts.sort_values(ascending=False)
assert ranked.iloc[9] > ranked.iloc[10], 'Ambiguous tie at top-ten boundary'
top = ranked.head(10)
# All entries after the first in original file order are superseded entries.
superseded_ids = amounts.loc[amounts['award_id'].duplicated(keep='first'), 'award_id'].unique()
selected = contracts[contracts['recipient_uei'].isin(top.index)]
answer = int(selected['award_id'].isin(superseded_ids).sum())
audit = top.to_frame().join(recipients.set_index('uei')['name'])
audit['contracts_with_superseded_amount'] = selected.assign(
    superseded=selected['award_id'].isin(superseded_ids)
).groupby('recipient_uei')['superseded'].sum()
audit.to_csv(OUT / 'recipient_counts.csv')
(OUT / 'answer.json').write_text(json.dumps({'answer': str(answer)}) + '\n')
print(audit.to_string())
print('Answer:', answer)
