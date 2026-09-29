import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
THRESHOLD = 10_000_000

def numeric_amount(value):
    text = str(value).strip().replace(',', '').replace('$', '')
    text = re.sub(r'\s*USD$', '', text, flags=re.I)
    match = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*([KMB]?)', text, flags=re.I)
    if not match:
        return float('nan')
    return float(match[1]) * {'': 1, 'K': 1e3, 'M': 1e6, 'B': 1e9}[match[2].upper()]

contracts = pd.read_parquet(ROOT / 'contracts_db/contracts.parquet')
amounts = pd.read_parquet(ROOT / 'contracts_db/contract_amounts.parquet').drop_duplicates('award_id', keep='first')
sectors = pd.read_parquet(ROOT / 'agencies_db/naics_sectors.parquet')
recipients = pd.read_parquet(ROOT / 'recipients_db/recipients.parquet')
contracts['code'] = contracts.naics_code.str.replace(r'^naics-', '', regex=True).str.replace('-', '', regex=False)
assert contracts.code.str.fullmatch(r'\d{6}').all()
contracts['sector'] = contracts.code.str[:2].map(sectors.set_index('code').sector)
assert contracts.sector.notna().all()
data = contracts.merge(amounts, on='award_id', how='left', validate='one_to_one')
assert data.amount_text.notna().all()
data['numeric_amount'] = data.amount_text.map(numeric_amount)
# Explicit magnitude statements suffice as witnesses for sector representation.
data['qualifies'] = data.numeric_amount.ge(THRESHOLD) | data.amount_text.str.contains(
    r'eight.figure|nine.figure|ten.figure|tens of millions|hundreds of millions|billion', case=False, regex=True)
represented = set(data.loc[data.qualifies, 'sector'])
evidence = data.loc[data.qualifies, ['award_id', 'sector', 'amount_text']].copy()
evidence.to_csv(OUT / 'explicit_evidence.csv', index=False)

# A complete recipient portfolio confined to one sector gives another sufficient
# witness: total > count * threshold implies at least one qualifying contract.
# Deduct half a displayed unit from abbreviated totals to allow for rounding.
portfolio = contracts.groupby('recipient_uei').agg(count=('award_id', 'size'), sector_count=('sector', 'nunique'), sector=('sector', 'first'))
portfolio = portfolio.merge(recipients, left_index=True, right_on='uei', validate='one_to_one')
portfolio['total'] = portfolio.total_amount_text.map(numeric_amount)
def rounding_margin(text):
    m = re.fullmatch(r'(\d+)(?:\.(\d+))?([KMB])', str(text).strip(), re.I)
    if not m:
        return 0
    return .5 * 10 ** (-len(m[2] or '')) * {'K': 1e3, 'M': 1e6, 'B': 1e9}[m[3].upper()]
portfolio['lower_total'] = portfolio.total - portfolio.total_amount_text.map(rounding_margin)
proof = portfolio[(portfolio.sector_count == 1) & (portfolio['count'] == portfolio.n_contracts) & (portfolio.lower_total >= portfolio['count'] * THRESHOLD)]
represented.update(proof.sector)
proof.to_csv(OUT / 'portfolio_evidence.csv', index=False)
(OUT / 'answer.json').write_text(json.dumps({'answer': str(len(represented))}) + '\n')
print('Qualifying sectors:', ', '.join(sorted(represented)))
print(json.dumps({'answer': str(len(represented))}))
