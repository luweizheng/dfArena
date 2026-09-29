import json,re
from pathlib import Path
import polars as pl
D=Path('/workspace/data')
c=pl.read_parquet(D/'contracts_db/contracts.parquet')
a=pl.read_parquet(D/'contracts_db/contract_amounts.parquet').unique('award_id',keep='first',maintain_order=True)
r=pl.read_parquet(D/'recipients_db/recipients.parquet')
assert c.join(a,on='award_id',how='anti').height==0
assert c.join(r,left_on='recipient_uei',right_on='uei',how='anti').height==0
assert r['uei'].n_unique()==r.height
j=c.join(r,left_on='recipient_uei',right_on='uei',validate='m:1').filter(pl.col('state').str.strip_chars().str.to_lowercase().is_in(['ca','california','calif.','calif'])).join(a,on='award_id',validate='m:1')
def classify(t):
 s=t.lower().replace('–','-')
 n=re.fullmatch(r'\s*\$?([\d,.]+)\s*([kmb])?\s*(?:usd)?\s*',s)
 if n:return float(n[1].replace(',',''))*{'k':1e3,'m':1e6,'b':1e9,None:1}[n[2]]>1e6
 if re.search(r'six.figure|five.figure|four.figure|hundreds.of.thousands|hundred thousand|sub-million|without breaching the million|not soaring to the seven|beneath the multimillion',s):return False
 if re.search(r'millions|seven.figure|eight.figure|nine.figure|multimillion|million-dollar engagements',s):return True
 return None
j=j.with_columns(pl.col('amount_text').map_elements(classify,return_dtype=pl.Boolean).alias('qualifies'))

# Recipient totals resolve vague amount descriptions for single-award UEIs.
# Multi-award cases are interpreted using the related amount descriptions:
# Northrop: $177m total, other award seven figures.
# Cynergy: $27m total, other two awards minor/five-figure.
# Spectrum: $5.7m total; two nurse-anesthetist service awards, three
# six-figure medical awards and one minor supply-budget award. The standard
# institutional healthcare award is in the same million-scale tier as its
# sibling nurse-anesthetist award.
def resolve(row):
    if row['qualifies'] is not None:
        text=row['amount_text'].lower()
        if 'below the seven-figure threshold' in text or 'without crossing into the millions' in text:
            return False
        return row['qualifies']
    if row['n_contracts']==1:
        result=classify(row['total_amount_text'])
        assert result is not None
        return result
    if classify(row['total_amount_text']) is False:
        return False
    text=row['amount_text'].lower()
    if any(phrase in text for phrase in [
        'substantial investment typical of large-scale engineering',
        'infusion akin to a mid-tier market expansion',
        'standard-tier investment typical for institutional healthcare',
    ]):
        return True
    # Remaining prose describes minor operational expenditures, small fees,
    # modest budgets, or lower six-digit sums; recipient totals corroborate
    # these where the recipient has less than $1m across all awards.
    assert any(word in text for word in [
        'modest','minor','small','minimal','trivial','pocket change','petty cash',
        'routine','entry-level','lower six-digit','six-digit','four-to-five','high-end consumer',
    ]), text
    return False
j=j.with_columns(pl.struct(pl.all()).map_elements(resolve,return_dtype=pl.Boolean).alias('qualifies'))
assert j['qualifies'].null_count()==0
j.write_csv('/workspace/work/classification.csv')
count=j.filter(pl.col('qualifies')).height
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':f'{count} contract awards.'})+'\n')
print(f'California awards: {j.height}; above $1,000,000: {count}')
