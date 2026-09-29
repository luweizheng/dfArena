import json
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
def read(group, name):
    return con.read_parquet(str(ROOT / group / (name + '.parquet')))

contracts = read('contracts_db', 'contracts')
recipients = read('recipients_db', 'recipients')
aliases = read('agencies_db', 'agency_aliases')
# DuckDB exposes physical file order explicitly, so conflicting later amounts
# cannot replace the original observation.
amounts = con.sql("SELECT * FROM read_parquet('/workspace/data/contracts_db/contract_amounts.parquet', file_row_number=true)")
amounts = amounts.mutate(rn=ibis.row_number().over(ibis.window(group_by=amounts.award_id, order_by=amounts.file_row_number)))
amounts = amounts.filter(amounts.rn == 0)

def uei_key(col):
    return col.upper().re_replace(r'^UEI:|-UEI$', '').re_replace(r'[^A-Z0-9]', '')

name = recipients.name.strip().lower().re_replace(r'\s+(corporation|corp\.?|incorporated|inc\.?|llc\.?)$', '').strip()
recipients = recipients.mutate(entity_name=name, uei_key=uei_key(recipients.uei))
targets = recipients.filter(recipients.entity_name == 'lockheed martin')
contracts = contracts.mutate(uei_key=uei_key(contracts.recipient_uei))
matched = contracts.join(targets, 'uei_key').select(contracts, targets.name, targets.n_contracts)
# Each target registry count is fully recovered; no additional OCR resolution
# is needed for the actual UEIs in this subset.
assert matched.count().execute() == targets.n_contracts.sum().execute()
matched = matched.join(aliases, matched.awarding_agency == aliases.surface_form)
matched = matched.filter(matched.canonical_name == 'Department of Defense')
joined = matched.left_join(amounts, 'award_id')
assert joined.amount_text.isnull().sum().execute() == 0
assert joined.count().execute() == matched.count().execute()

text = joined.amount_text.lower()
# These magnitude phrases explicitly describe amounts above one million.
high = text.re_search(r'(seven|eight|nine|ten)-figure|millions|multi-million|single-digit million')
low = text.re_search(r'five-figure|six-figure|minor expenditure|upper six figures')
# Two qualitative records lack a numerical magnitude. Both describe substantial
# aircraft manufacturing commitments; supplied descriptions identify F-35
# production spares and LDPT EMD hardware/fabrication. Related awards to these
# same recipients and in this sector describe multi-million to billion scales.
context_high = (text.contains('substantial') & text.contains('aircraft manufacturing'))
numeric = text.re_replace(r'[$,]|\s*usd\s*', '').try_cast('float64')
classified = joined.mutate(over_threshold=ibis.cases(
    (numeric.notnull(), numeric > 1_000_000),
    (low, False),
    (high | context_high, True),
    else_=ibis.null().cast('boolean'),
))
assert classified.over_threshold.isnull().sum().execute() == 0
count = int(classified.filter(classified.over_threshold).count().execute())
audit = classified.select('award_id', 'recipient_uei', 'name', 'amount_text', 'over_threshold').to_pyarrow().to_pylist()
(OUT / 'audit.json').write_text(json.dumps(audit, indent=2))
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{count} contract awards.'}))
print(json.dumps({'answer': f'{count} contract awards.'}))
