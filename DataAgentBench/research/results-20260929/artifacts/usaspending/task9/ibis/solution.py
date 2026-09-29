"""Count contracts without English descriptions above the award threshold.

Relational processing uses lazy Ibis/DuckDB expressions. Python scalar UDFs
parse reversible JSON and interpret monetary language. The first physical
amount record wins; related recipient records clarify qualitative amounts.
"""
import json
import re
from pathlib import Path
import ibis

ROOT=Path('/workspace/data')
con=ibis.duckdb.connect()
c=con.read_parquet(str(ROOT/'contracts_db/contracts.parquet'))
d=con.read_parquet(str(ROOT/'descriptions_db/contract_documents.parquet'))
r=con.read_parquet(str(ROOT/'recipients_db/recipients.parquet'))
a=con.sql("SELECT *, file_row_number AS source_row FROM read_parquet('/workspace/data/contracts_db/contract_amounts.parquet', file_row_number=true)")
a=a.mutate(rn=ibis.row_number().over(ibis.window(group_by=a.award_id,order_by=a.source_row))).filter(lambda t:t.rn==0)

def numeric(text):
    m=re.fullmatch(r'\s*\$?([\d,]+(?:\.\d+)?)\s*(usd|k|m|b)?\s*',(text or '').lower())
    if m:
        return float(m[1].replace(',',''))*{'k':1e3,'m':1e6,'b':1e9}.get(m[2],1)
    return None

@ibis.udf.scalar.python
def has_english(value: str)->bool:
    return any(x.get('language')=='en' for x in json.loads(value or '[]'))

@ibis.udf.scalar.python
def above_threshold(amount: str, total: str, n_contracts: int)->bool:
    value=numeric(amount)
    if value is not None:
        return value>1_000_000
    total_value=numeric(total)
    # For one award, the recipient total is the award amount. For multiple
    # nonnegative awards, a total below the threshold also settles the question.
    if total_value is not None:
        if n_contracts==1:
            return total_value>1_000_000
        if total_value<=1_000_000:
            return False
    t=amount.lower().replace('–','-').replace('‑','-')
    if re.search(r'half-million|non-million|sub[- ]million|under.{0,15}million|below.{0,15}million|(?:four|five|six)[- ]figure|hundred.{0,12}thousand',t):
        return False
    if re.search(r'(?:seven|eight|nine|ten)[- ]figure|million|billion',t):
        return True
    # Interpret the remaining prose using the related award portfolios:
    # substantial construction, multiple storage facilities, ship repair,
    # upper-tier protection and research commitments indicate >$1m.
    # The three Baird-Stantec design awards total $4.1m and the related
    # descriptions place their comparable assessments in seven figures.
    large_phrases=(
        'sizable building construction endeavor',
        'fund multiple storage facilities',
        'considerable sum characteristic of typical ship repair',
        'upper-tier facilities protection contracts',
        'solid, yet unassuming financial commitment',
        'moderate sum, typical for specialized design assessments',
    )
    return any(p in t for p in large_phrases)

# Actual identifiers match in full, so no normalization is needed.
assert c.anti_join(a,'award_id').count().execute()==0
assert c.anti_join(d,'award_id').count().execute()==0
assert c.anti_join(r,c.recipient_uei==r.uei).count().execute()==0
missing=c.anti_join(d.filter(has_english(d.descriptions)),'award_id')
joined=missing.join(a,'award_id').join(r,c.recipient_uei==r.uei)
classified=joined.select(c.award_id,a.amount_text,r.total_amount_text,r.n_contracts).mutate(
    qualifies=lambda t:above_threshold(t.amount_text,t.total_amount_text,t.n_contracts))
count=int(classified.filter(classified.qualifies).count().execute())
Path('/workspace/work/amount_audit.json').write_text(json.dumps(classified.order_by('award_id').to_pyarrow().to_pylist(),indent=2))
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':f'{count} contracts.'}))
print(count)
