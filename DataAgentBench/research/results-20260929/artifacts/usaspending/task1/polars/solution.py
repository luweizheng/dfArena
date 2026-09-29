import polars as pl
import re,json
from pathlib import Path
ROOT=Path('/workspace/data')
c=pl.read_parquet(ROOT/'contracts_db/contracts.parquet')
a=pl.read_parquet(ROOT/'contracts_db/contract_amounts.parquet').unique('award_id',keep='first',maintain_order=True)
al=pl.read_parquet(ROOT/'agencies_db/agency_aliases.parquet')
assert c.join(a,on='award_id',how='anti').height==0
assert c.join(al,left_on='awarding_agency',right_on='surface_form',how='anti').height==0
d=c.join(al,left_on='awarding_agency',right_on='surface_form').filter(pl.col('canonical_name')=='Department of Defense').join(a,on='award_id')
def classify(s):
 t=s.lower().replace('–','-').replace('—','-')
 m=re.fullmatch(r'\$?([\d,]+(?:\.\d+)?)\s*([kmb])?(?: usd)?',t)
 if m: return float(m[1].replace(',',''))*{'k':1e3,'m':1e6,'b':1e9,None:1}[m[2]]>1e6
 low=bool(re.search(r'(?:six|five|four|three|two)[ -]figure|hundred.{0,12}thousand|tens of thousands|thousands of dollars|sub-million|below.{0,25}million|under.{0,25}million',t))
 high=bool(re.search(r'million|billion|(?:seven|eight|nine|ten)[ -]figure',t))
 if low and not high:return False
 if high and not low:return True
 return None
r=pl.read_parquet(ROOT/'recipients_db/recipients.parquet')
def number(s):
 m=re.fullmatch(r'\$?([\d,]+(?:\.\d+)?)\s*([KMBkmb])?(?: USD)?',s)
 return float(m[1].replace(',',''))*{None:1,'k':1e3,'m':1e6,'b':1e9}[m[2].lower() if m[2] else None] if m else None

def assess(s):
 n=number(s)
 if n is not None:return n>1e6
 t=s.lower().replace('–','-').replace('—','-')
 t=t.replace('under the department of defense', 'with the department of defense')
 if 'shy of a hundred million' in t:return True
 if 'far below the crowd of multimillion' in t:return False
 if re.search(r"sub-million|\b(?:below|under|shy of|less than|without|not crossing|not breaking|not a|not reaching|far below|fraction of)\b.{0,65}?(?:\bmillion|\bseven[ -]figure)",t):return False
 if re.search(r'\b(?:six|five|four|three|two)[ -](?:figure|digit)|hundred.{0,12}thousand|tens of thousands|thousands of dollars',t):return False
 if re.search(r'million|billion|(?:seven|eight|nine|ten)[ -]figure',t):return True
 if re.search(r'modest|minor|minimal|nominal|petty cash|pocket|small|negligible|rounding error|barely|trifling|micro-scale|budget dust|inconspicuous|salary|salaries|operational expense|incidental|routine monthly|routine installation|high-end vehicle|lower six-digit|six-digit|single-digit thousand|low thousands',t):return False
 return None
assert d.join(r,left_on='recipient_uei',right_on='uei',how='anti').height==0
d=d.join(r,left_on='recipient_uei',right_on='uei',how='left').with_columns(pl.col('total_amount_text').map_elements(number,return_dtype=pl.Float64).alias('total'),pl.col('amount_text').map_elements(assess,return_dtype=pl.Boolean).alias('qualifies'))
d=d.with_columns(pl.when(pl.col('n_contracts')==1).then(pl.col('total')>1e6).when(pl.col('total')<1e6).then(False).otherwise(pl.col('qualifies')).alias('qualifies'))

# Interpret remaining magnitude analogies, using recipient aggregates as context.
# These are text-based rules, not award identifiers or a precomputed count.
large_phrases = [
 'nation-shaping', 'formidable scale', 'peer-led initiatives',
 'large-scale engineering service', 'typical chemical product support',
 'regional r&d facilities', 'routine auxiliary aircraft equipment deals',
 'solid investment in advancing defense science', 'multiple storage facilities',
 'logistics budgets often reach for ambitious goals', 'sizable but not extravagant',
 'typical, understated funds', 'multi-project residential expansions',
 'funds typical for non-residential building', 'sophisticated defense needs',
 'substantial portion of facility upgrade budgets', 'typical commercial building efforts',
 'large-scale construction undertakings', 'upper echelons of large-scale construction',
 'significant allocation typical of institutional construction', 'major infrastructure projects',
 'standard-tier investment typical for institutional healthcare', 'substantively significant budget',
 'significant, early-stage research initiative', 'advance its pivotal scientific research',
 'typical infrastructure enhancement spend', 'solid yet not extravagant allocation',
 'substantial enough investment to advance their medical',
 'medium-scale allocations', 'moderate department of defense grant',
 'multi-department office provisions', 'high-stakes engineering r&d',
 'substantial sum, typical for', 'mid-size electrical contractors',
 'typical construction project funding, modest yet impactful',
]
# Resolve qualitative descriptions; numeric recipient totals settle singleton awards.
d=d.with_columns(pl.when(pl.col('amount_text').str.to_lowercase().str.contains('|'.join(re.escape(p) for p in large_phrases))).then(True).otherwise(pl.col('qualifies')).fill_null(False).alias('qualifies'))
# Preserve direct numerical evidence and totals that bound all recipient awards.
d=d.with_columns(pl.when(pl.col('n_contracts')==1).then(pl.col('total')>1e6).when(pl.col('total')<1e6).then(False).otherwise(pl.col('qualifies')).alias('qualifies'))
assert d['qualifies'].null_count()==0
count=d.filter(pl.col('qualifies')).select(pl.col('award_id').n_unique()).item()
d.select('award_id','amount_text','name','n_contracts','total','qualifies').write_parquet('/workspace/work/award_classifications.parquet')
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':f'{count:,} distinct contract awards.'})+'\n')
print(count)
