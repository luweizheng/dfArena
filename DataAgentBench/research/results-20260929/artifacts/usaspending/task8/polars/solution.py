import json
import re
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
def read(group, table):
    return pl.read_parquet(DATA / group / f'{table}.parquet')

def entity_name(name):
    name = name.strip().lower()
    # Remove trailing corporate suffixes only; preserve internal punctuation.
    return re.sub(r'(?:\s+(?:corporation|corp\.?|incorporated|inc\.?|llc|l\.l\.c\.?|ltd\.?))+$', '', name).strip()

contracts = read('contracts_db', 'contracts')
recipients = read('recipients_db', 'recipients').with_columns(
    pl.col('name').map_elements(entity_name, return_dtype=pl.String).alias('entity'))
amounts = read('contracts_db', 'contract_amounts').unique('award_id', keep='first', maintain_order=True)
aliases = read('agencies_db', 'agency_aliases')
assert aliases['surface_form'].n_unique() == aliases.height
assert contracts.join(recipients, left_on='recipient_uei', right_on='uei', how='anti').is_empty()
selected = (contracts.join(recipients.filter(pl.col('entity') == 'lockheed martin'),
                           left_on='recipient_uei', right_on='uei', validate='m:1')
            .join(aliases, left_on='awarding_agency', right_on='surface_form', how='left', validate='m:1'))
assert selected['canonical_name'].null_count() == 0
selected = selected.filter(pl.col('canonical_name') == 'Department of Defense').join(
    amounts, on='award_id', how='left', validate='m:1')
assert selected['amount_text'].null_count() == 0

def explicit_magnitude(text):
    text = text.lower()
    numeric = re.fullmatch(r'\s*\$?([\d,.]+)\s*([kmb])?\s*(?:usd)?\s*', text)
    if numeric:
        value = float(numeric[1].replace(',', '')) * {'k': 1e3, 'm': 1e6, 'b': 1e9, None: 1}[numeric[2]]
        return value > 1_000_000
    if any(term in text for term in ['five-figure', 'six-figure', 'small office supply purchase']):
        return False
    if any(term in text for term in ['seven-figure', 'eight-figure', 'nine-figure', 'ten-figure',
                                     'millions', 'multi-million', 'single-digit million']):
        return True
    return None

selected = selected.with_columns(pl.col('amount_text').map_elements(explicit_magnitude, return_dtype=pl.Boolean).alias('explicit_above'))
# The two less explicit descriptions compare the award to this recipient's
# typical Defense aircraft-manufacturing commitments. Resolve them using
# the explicitly described awards in that same supplied cohort.
cohort = selected.filter((pl.col('naics_code') == '336411') & pl.col('explicit_above').is_not_null())
assert cohort.height > 0 and cohort['explicit_above'].all()
results = []
for row in selected.iter_rows(named=True):
    above = row['explicit_above']
    basis = 'numeric or qualitative magnitude'
    if above is None:
        text = row['amount_text'].lower()
        assert row['naics_code'] == '336411'
        assert 'substantial' in text and ('routinely' in text or 'typical' in text)
        above = bool(cohort['explicit_above'].all())
        basis = 'typical substantial aircraft-manufacturing commitment; all explicit same-recipient Defense cohort amounts exceed threshold'
    results.append({**row, 'above_threshold': above, 'classification_basis': basis})
audit = pl.DataFrame(results)
audit.write_csv(OUT / 'award_audit.csv')
count = audit.filter(pl.col('above_threshold')).height
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{count} contract awards.'}) + '\n')
print(json.dumps({'answer': f'{count} contract awards.'}))
