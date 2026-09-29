import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def numeric(text):
    s = str(text).strip().upper().replace('USD', '').replace('$', '').replace(',', '').strip()
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*([KMB]?)', s)
    if not m:
        return None
    return float(m[1]) * {'': 1, 'K': 1e3, 'M': 1e6, 'B': 1e9}[m[2]]

contracts = pd.read_parquet(DATA / 'contracts_db/contracts.parquet')
recipients = pd.read_parquet(DATA / 'recipients_db/recipients.parquet')
amounts = pd.read_parquet(DATA / 'contracts_db/contract_amounts.parquet')
# Preserve file order when discarding the deliberately conflicting later records.
amounts = amounts.drop_duplicates('award_id', keep='first')
assert contracts.award_id.isin(amounts.award_id).all()
assert contracts.recipient_uei.isin(recipients.uei).all()
joined = contracts.merge(recipients, left_on='recipient_uei', right_on='uei', validate='many_to_one').merge(amounts, on='award_id', validate='one_to_one')
ca = joined[joined.state.str.strip().str.lower().isin(['ca', 'california', 'calif.', 'calif'])].copy()

low = re.compile(r'(?:six|five|four|three)[ -](?:figure|digit)|hundred.{0,12}thousand|sub-million|under.{0,15}million|below.{0,15}million|beneath.{0,15}million|without breaching the million|not soaring to the seven|high thousands|below the seven-figure|without crossing into the millions')
high = re.compile(r'(?:seven|eight|nine|ten)[ -]figure|million|billion')

def classify(row):
    value = numeric(row.amount_text)
    if value is not None:
        return value > 1_000_000, 'numeric award amount'
    total = numeric(row.total_amount_text)
    if row.n_contracts == 1 and total is not None:
        return total > 1_000_000, 'single-award recipient total'
    t = row.amount_text.lower()
    if low.search(t):
        return False, 'explicit magnitude below threshold'
    if high.search(t):
        return True, 'explicit magnitude above threshold'
    if total is not None and total <= 1_000_000:
        return False, 'recipient total below threshold'
    # Related records support these otherwise imprecise magnitude descriptions:
    # Northrop total 177.3M with one other seven-figure award; Cynergy total
    # 27.48M with two minor awards; Spectrum total 5.7M with a lower-million
    # award, three six-figure awards, and one minor supplies award.
    if any(p in t for p in ['substantial investment typical of large-scale engineering',
                             'mid-tier market expansion investment',
                             'standard-tier investment typical for institutional healthcare']):
        return True, 'qualitative scale supported by related recipient records'
    # Remaining descriptions describe minor retainers, modest budget segments,
    # petty cash, routine supplies, and similarly small engagements.
    return False, 'qualitative minor or modest expenditure'

assessments = ca.apply(classify, axis=1)
ca['over_threshold'] = assessments.map(lambda x: x[0])
ca['reason'] = assessments.map(lambda x: x[1])
ca.to_csv(OUT / 'award_assessment.csv', index=False)
count = int(ca.over_threshold.sum())
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{count} contract awards.'}) + '\n')
print(count)
print(ca.groupby(['reason', 'over_threshold']).size().to_string())
