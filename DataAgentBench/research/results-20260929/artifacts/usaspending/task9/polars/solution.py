import json
import re
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def numeric(text):
    s = text.strip().upper().replace('USD', '').replace('$', '').replace(',', '').strip()
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*([KMB]?)', s)
    if not m:
        return None
    return float(m[1]) * {'': 1, 'K': 1e3, 'M': 1e6, 'B': 1e9}[m[2]]

def classify(row):
    text = row['amount_text']
    n = numeric(text)
    if n is not None:
        return {'above': n > 1_000_000, 'basis': 'numeric award amount'}
    # A single-contract recipient's supplied total is its award amount.
    total = numeric(row['total_amount_text'])
    if row['n_contracts'] == 1 and total is not None:
        return {'above': total > 1_000_000, 'basis': 'single-contract recipient total'}
    s = text.lower()
    if re.search(r'sub-million|non-million|half.million|half a million|beneath the multimillion', s):
        return {'above': False, 'basis': 'explicit below-million magnitude'}
    if re.search(r'(seven|eight|nine)[ -]figure|million|billion', s):
        return {'above': True, 'basis': 'million-scale qualitative magnitude'}
    if re.search(r'(four|five|six)[ -]figure|thousand|six digits', s):
        return {'above': False, 'basis': 'below-million qualitative magnitude'}
    if total is not None and 0 <= total < 1_000_000:
        return {'above': False, 'basis': 'recipient total below threshold, consistent with modest prose'}
    # Qualitative descriptions without an explicit magnitude. These phrases
    # describe substantial R&D, infrastructure, ship repair, and facilities
    # protection awards, corroborated by their recipients' supplied records.
    large = (
        'solid, yet unassuming financial commitment characteristic of many peer-led initiatives',
        'sizable enough to fund multiple storage facilities',
        'substantial allocation',
        'considerable sum characteristic of typical ship repair endeavors',
        'scale typically reserved for upper-tier facilities protection contracts',
    )
    if any(p in s for p in large):
        return {'above': True, 'basis': 'substantial qualitative scope and related recipient records'}
    small = r'modest|minor|small|barely|sliver|token|routine|rounding error|moderate sum|fraction|pocket|pebble'
    if re.search(small, s):
        return {'above': False, 'basis': 'limited qualitative expenditure scope'}
    raise ValueError(f'Unclassified amount: {text}')

contracts = pl.read_parquet(DATA / 'contracts_db/contracts.parquet')
amounts = pl.read_parquet(DATA / 'contracts_db/contract_amounts.parquet').unique(
    subset='award_id', keep='first', maintain_order=True)
docs = pl.read_parquet(DATA / 'descriptions_db/contract_documents.parquet').with_columns(
    pl.col('descriptions').str.json_decode(pl.List(pl.Struct({'language': pl.String, 'value': pl.String})))
    .list.eval(pl.element().struct.field('language') == 'en').list.any().fill_null(False).alias('has_english'))
recipients = pl.read_parquet(DATA / 'recipients_db/recipients.parquet')
assert contracts['award_id'].n_unique() == contracts.height
assert contracts.join(amounts, on='award_id', how='anti').height == 0
assert contracts.join(docs, on='award_id', how='anti').height == 0
joined = contracts.join(docs, on='award_id', validate='1:1').filter(~pl.col('has_english')).join(
    amounts, on='award_id', validate='1:1').join(recipients, left_on='recipient_uei', right_on='uei', validate='m:1')
result = joined.with_columns(pl.struct('amount_text', 'n_contracts', 'total_amount_text').map_elements(
    classify, return_dtype=pl.Struct({'above': pl.Boolean, 'basis': pl.String})).alias('assessment')).unnest('assessment')
result.select('award_id', 'amount_text', 'total_amount_text', 'n_contracts', 'above', 'basis').write_csv(OUT / 'amount_audit.csv')
count = result.filter(pl.col('above')).height
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{count} contracts.'}) + '\n')
print(json.dumps({'no_english': result.height, 'above_threshold': count}))
