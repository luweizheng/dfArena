import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
contracts = pd.read_parquet(DATA / 'contracts_db/contracts.parquet', columns=['recipient_uei', 'naics_code'])
sectors = pd.read_parquet(DATA / 'agencies_db/naics_sectors.parquet')
recipients = pd.read_parquet(DATA / 'recipients_db/recipients.parquet', columns=['uei'])

# Observed NAICS representations are six digits, naics- prefixed,
# or separated with a hyphen after the two-digit sector.
codes = contracts['naics_code'].str.replace(r'(?i)^naics-', '', regex=True).str.replace('-', '', regex=False)
assert codes.str.fullmatch(r'\d{6}').all()
sector_map = sectors.set_index('code')['sector']
contract_sectors = codes.str[:2].map(sector_map)
assert contract_sectors.notna().all()

# Every contract UEI matches the recipient registry directly. Normalize
# observed wrappers/case while preserving separate UEIs for the same company.
assert contracts['recipient_uei'].isin(recipients['uei']).all()
ueis = contracts['recipient_uei'].str.upper().str.replace(r'^UEI:|-UEI$', '', regex=True)
assert ueis.nunique() == contracts['recipient_uei'].nunique()
count = int(ueis[contract_sectors.eq('33')].nunique())
answer = {'answer': f'{count} distinct recipient UEIs.'}
Path('/workspace/work/answer.json').write_text(json.dumps(answer) + '\n')
print(json.dumps(answer))
