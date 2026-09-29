import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')

def name_key(value):
    value = value.strip().casefold()
    suffix = r'(?:,?\s+)(?:corporation|corp\.?|incorporated|inc\.?|llc|l\.l\.c\.?|ltd\.?)$'
    while re.search(suffix, value):
        value = re.sub(suffix, '', value).rstrip()
    return value

contracts = pd.read_parquet(ROOT / 'contracts_db/contracts.parquet')
recipients = pd.read_parquet(ROOT / 'recipients_db/recipients.parquet')
amounts = pd.read_parquet(ROOT / 'contracts_db/contract_amounts.parquet')
aliases = pd.read_parquet(ROOT / 'agencies_db/agency_aliases.parquet')
documents = pd.read_parquet(ROOT / 'descriptions_db/contract_documents.parquet')
assert contracts.recipient_uei.isin(recipients.uei).all()
assert contracts.award_id.isin(amounts.award_id).all()
# Preserve the original first amount, including when later entries conflict.
amounts = amounts.drop_duplicates('award_id', keep='first')
agency_map = aliases.set_index('surface_form').canonical_name
contracts['canonical_agency'] = contracts.awarding_agency.map(agency_map)
assert contracts.canonical_agency.notna().all()
ueis = recipients.loc[recipients.name.map(name_key).eq('lockheed martin'), 'uei']
selected = contracts.loc[contracts.recipient_uei.isin(ueis) & contracts.canonical_agency.eq('Department of Defense')].copy()
selected = selected.merge(amounts, on='award_id', validate='many_to_one').merge(documents, on='award_id', validate='many_to_one')

def explicit_amount(text):
    s = text.strip().lower().replace(',', '').replace('$', '').replace('usd', '').strip()
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*([kmb])?', s)
    if m:
        return float(m[1]) * {'k': 1e3, 'm': 1e6, 'b': 1e9, None: 1}[m[2]] > 1e6
    if re.search(r'(?:five|six)-figure|small office supply|sub-million', text.lower()):
        return False
    if re.search(r'(?:seven|eight|nine|ten)-figure|millions|multi-million|single-digit million', text.lower()):
        return True
    return None

selected['qualifies'] = selected.amount_text.map(explicit_amount)
selected['basis'] = 'Numeric amount or stated monetary magnitude'
for idx, row in selected[selected.qualifies.isna()].iterrows():
    # Resolve vague substantial aircraft commitments against supplied related
    # awards for the same UEI and aircraft-manufacturing category.
    sector = re.sub(r'\D', '', row.naics_code)
    peers = selected[(selected.recipient_uei == row.recipient_uei) & selected.naics_code.str.replace(r'\D', '', regex=True).eq(sector) & selected.qualifies.notna()]
    description = ' '.join(d['value'] for d in json.loads(row.descriptions)).lower()
    assert sector == '336411' and len(peers) > 0 and peers.qualifies.all()
    assert re.search(r'substantial|robust', row.amount_text, re.I)
    assert re.search(r'hardware|aircraft', description)
    selected.loc[idx, 'qualifies'] = True
    selected.loc[idx, 'basis'] = 'Substantial aircraft commitment; related same-UEI aircraft awards exceed $1 million, supported by hardware/production description'
assert selected.qualifies.notna().all()
count = int(selected.qualifies.sum())
selected.to_csv(OUT / 'award_audit.csv', index=False)
with (OUT / 'answer.json').open('w') as f:
    json.dump({'answer': f'{count} contract awards.'}, f)
print(json.dumps({'answer': f'{count} contract awards.'}))
