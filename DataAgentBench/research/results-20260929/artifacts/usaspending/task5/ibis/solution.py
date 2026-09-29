import json
from pathlib import Path
import ibis

ROOT = Path('/workspace/data')
con = ibis.duckdb.connect()
contracts = con.read_parquet(str(ROOT / 'contracts_db/contracts.parquet'))
# DuckDB exposes the original physical Parquet row ordinal explicitly.
amounts = con.sql("SELECT *, file_row_number AS original_row FROM read_parquet('/workspace/data/contracts_db/contract_amounts.parquet', file_row_number=true)")
amounts = amounts.mutate(rn=ibis.row_number().over(ibis.window(group_by='award_id', order_by='original_row')))
amounts = amounts.filter(amounts.rn == 0)
sectors = con.read_parquet(str(ROOT / 'agencies_db/naics_sectors.parquet'))
contracts = contracts.mutate(sector_code=contracts.naics_code.re_replace(r'[^0-9]', '').substr(0, 2))
joined = contracts.join(amounts, 'award_id').join(sectors, contracts.sector_code == sectors.code)
s = joined.amount_text.lower()
def parse_amount(text):
    clean = text.lower().re_replace(r'[$,\s]', '').re_replace(r'usd$', '')
    factor = ibis.cases((clean.endswith('k'), 1000), (clean.endswith('m'), 1000000), (clean.endswith('b'), 1000000000), else_=1)
    return clean.re_replace(r'[kmb]$', '').try_cast('decimal(24,2)') * factor

numeric = parse_amount(s)
# Explicit magnitude descriptions give a sufficient lower bound for qualification.
qualifies = (numeric >= 10000000).fill_null(False) | s.re_search(r'(eight|nine|ten|eleven|8|9|10|11)[ -]figure|tens of millions|hundreds of millions|billion')
joined = joined.mutate(qualifies=qualifies)
summary = joined.group_by('sector').aggregate(total=ibis._.count(), qualifying=ibis._.qualifies.sum()).order_by('sector')
print(summary.to_pyarrow().to_pylist())
remaining = joined.filter(~joined.sector.isin(joined.filter(joined.qualifies).sector)).select('award_id','sector','amount_text')
Path('/workspace/work/remaining.json').write_text(json.dumps(remaining.to_pyarrow().to_pylist(), indent=2))
# A recipient whose complete set of contracts belongs to one sector and whose
# total exceeds n * threshold proves that sector is represented, even when
# individual qualitative amounts do not provide an exact value.
recipients = con.read_parquet(str(ROOT / 'recipients_db/recipients.parquet'))
def normalize_uei(value):
    return value.upper().re_replace(r'^UEI:', '').re_replace(r'-UEI$', '')
r = recipients.mutate(uei_key=normalize_uei(recipients.uei), total=parse_amount(recipients.total_amount_text))
j = joined.mutate(uei_key=normalize_uei(joined.recipient_uei))
g = j.group_by('uei_key').aggregate(observed=ibis._.count(), sector_count=ibis._.sector.nunique(), sector=ibis._.sector.min())
proof = g.join(r, 'uei_key')
proof = proof.filter((proof.sector_count == 1) & (proof.observed == proof.n_contracts) & (proof.total >= proof.n_contracts * 10000000))
represented = joined.filter(joined.qualifies).select('sector').union(proof.select('sector'), distinct=True)
print('Recipient-total proofs:', proof.select('name', 'sector', 'observed', 'total').to_pyarrow().to_pylist())
count = represented.sector.nunique().execute()
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': str(count)}))
print('Answer:', count)
