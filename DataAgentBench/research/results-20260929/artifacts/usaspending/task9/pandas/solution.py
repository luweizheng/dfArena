"""Count awards without an English description and above one million dollars.

Pandas performs all loading, joining and counting. Qualitative amounts are
interpreted by magnitude language; recipient totals support vague wording.
The first amount row is authoritative, as required by the supplied hints.
"""
import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
LIMIT = 1_000_000


def numeric_amount(text):
    s = str(text).upper().replace('USD', '').replace('$', '').replace(',', '').strip()
    match = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*([KMB]?)', s)
    if not match:
        return None
    return float(match[1]) * {'': 1, 'K': 1000, 'M': 1_000_000, 'B': 1_000_000_000}[match[2]]


def classify(row):
    amount = numeric_amount(row.amount_text)
    if amount is not None:
        return amount > LIMIT, 'numeric award amount'
    total = numeric_amount(row.total_amount_text)
    if row.n_contracts == 1:
        assert total is not None
        return total > LIMIT, 'single-contract recipient total'
    s = row.amount_text.lower().replace('‑', '-').replace('–', '-')
    below = (r'(?:four|five|six)[ -]figure|upper range of six digits|'
             r'hundred.{0,15}thousand|thousands|sub-million|non-million|'
             r'under.{0,10}million|beneath.{0,10}million|shy.{0,20}million|'
             r'without.{0,20}million')
    if re.search(below, s):
        return False, 'qualitative magnitude below threshold'
    if re.search(r'(?:seven|eight|nine|ten)[ -]figure|million|billion', s):
        return True, 'qualitative magnitude above threshold'
    # For recipients with multiple contracts, a total below the threshold
    # corroborates the small allocations described in the award prose.
    if total is not None and total <= LIMIT:
        return False, 'small award wording corroborated by recipient total'
    # These phrases describe substantial research, construction, storage,
    # ship repair, and security awards. Related recipient portfolios inspected
    # in the supplied data are in the millions and corroborate that scale.
    substantial = (r'solid, yet unassuming financial commitment|'
                   r'sizable enough to fund multiple storage facilities|'
                   r'substantial allocation.*sizable building construction|'
                   r'considerable sum characteristic of typical ship repair|'
                   r'upper-tier facilities protection contracts')
    if re.search(substantial, s):
        assert total is not None and total > LIMIT
        return True, 'substantial award wording corroborated by recipient portfolio'
    small = (r'modest|minor|small-scale|small in scale|smaller financial gesture|small, almost inconsequential|small office|typical office administrative|'
             r'rounding error|trivial|barely|sliver|routine checklist|'
             r'moderate sum, typical for specialized design assessments')
    if re.search(small, s):
        return False, 'qualitative description of a small or moderate allocation'
    raise ValueError(f'Unresolved qualitative amount: {row.award_id}: {row.amount_text}')


def main():
    contracts = pd.read_parquet(DATA / 'contracts_db/contracts.parquet')
    amounts = pd.read_parquet(DATA / 'contracts_db/contract_amounts.parquet')
    docs = pd.read_parquet(DATA / 'descriptions_db/contract_documents.parquet')
    recipients = pd.read_parquet(DATA / 'recipients_db/recipients.parquet')
    amounts = amounts.drop_duplicates('award_id', keep='first')
    assert contracts.award_id.is_unique and docs.award_id.is_unique
    assert set(contracts.award_id) == set(amounts.award_id) == set(docs.award_id)
    docs['has_english'] = docs.descriptions.map(
        lambda value: any(d.get('language') == 'en' for d in json.loads(value)))
    joined = contracts.merge(amounts, on='award_id', validate='one_to_one').merge(
        docs[['award_id', 'has_english']], on='award_id', validate='one_to_one')
    candidates = joined.loc[~joined.has_english].copy()
    candidates = candidates.merge(recipients[['uei', 'n_contracts', 'total_amount_text']],
                                  left_on='recipient_uei', right_on='uei',
                                  how='left', validate='many_to_one')
    assert candidates.n_contracts.notna().all()
    decisions = candidates.apply(classify, axis=1)
    candidates['above_threshold'] = decisions.map(lambda pair: pair[0])
    candidates['reason'] = decisions.map(lambda pair: pair[1])
    candidates.to_csv(OUT / 'decision_audit.csv', index=False)
    count = int(candidates.above_threshold.sum())
    (OUT / 'answer.json').write_text(json.dumps({'answer': f'{count} contracts.'}) + '\n')
    print(json.dumps({'without_english': len(candidates), 'qualifying': count}))


if __name__ == '__main__':
    main()
