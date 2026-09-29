import json,re
from pathlib import Path
import polars as pl
D=Path('/workspace/data')
def classify(text):
 s=text.lower().replace('‑','-').replace('–','-')
 n=re.fullmatch(r'\s*\$?([\d,]+(?:\.\d+)?)\s*([kmb])?\s*(?:usd|dollars)?\s*',s)
 if n:return float(n[1].replace(',',''))*{'k':1e3,'m':1e6,'b':1e9,None:1}[n[2]]>1e6
 if re.search(r'(?:sub|below|under)[ -]million|(?:four|five|six)[ -]figure|hundreds of thousands|tens of thousands|petty cash|without breaching the million|without stretching into the million',s):return False
 if re.search(r'(?:seven|eight|nine|ten)[ -]figure|millions|multi[ -]?million|billion|mid-million',s):return True
 if re.search(r'hundred[ -]thousand|hundreds-of-thousands|six-digit|thousands|half.million|shy of.*million|below.*million|under.*million',s):return False
 if re.search(r'low-to-mid million|several million|few million|single-digit million|seven-digit',s):return True
 if re.search(r'minor|small|pocket|barely|nominal|minimal|micro-scale|entry-level|routine monthly|salary|rounding error|negligible|brief|mere whisper|few good laptops',s):return False
 # Narrow contextual descriptions of expenditures below a million dollars.
 if re.search(r'several high-end consumer vehicles|several annual salaries|single advanced care bed|mid-range vehicle|short-term office equipment leases|blueprint draft|initial equipment assessment|early-stage design consultations|initial feasibility studies|routine wiring installations|routine hvac adjustments|quick-turnaround print|modest engineering consultation|modest outlay typical for testing|modest investment aligned with routine consulting|lower end of procurement',s):return False
 return None
c=pl.read_parquet(D/'contracts_db/contracts.parquet')
a=pl.read_parquet(D/'contracts_db/contract_amounts.parquet').unique('award_id',keep='first',maintain_order=True)
al=pl.read_parquet(D/'agencies_db/agency_aliases.parquet')
x=c.join(a,on='award_id',how='left',validate='m:1').join(al,left_on='awarding_agency',right_on='surface_form',how='left',validate='m:1').with_columns(pl.col('amount_text').map_elements(classify,return_dtype=pl.Boolean).alias('above'))
assert x['canonical_name'].null_count()==0
assert x['amount_text'].null_count()==0
stats=x.group_by('canonical_name').agg(pl.len().alias('n'),pl.col('above').sum().alias('yes'),pl.col('above').is_null().sum().alias('unknown')).filter(pl.col('n')>=10).with_columns((pl.col('yes')/pl.col('n')).alias('lower'),((pl.col('yes')+pl.col('unknown'))/pl.col('n')).alias('upper')).sort('lower',descending=True)
print(stats)
x.filter(pl.col('above').is_null()).write_json('/workspace/work/unknown.json')
stats.write_csv('/workspace/work/bounds.csv')

# Select only when the winner is guaranteed even under the most favorable
# interpretation of every unresolved amount for competing agencies.
from fractions import Fraction
rows=stats.to_dicts()
rows.sort(key=lambda r:(-Fraction(r['yes'],r['n']),r['canonical_name']))
winner=rows[0]
for rival in rows[1:]:
 low=Fraction(winner['yes'],winner['n'])
 high=Fraction(rival['yes']+rival['unknown'],rival['n'])
 assert low>high or (low==high and winner['canonical_name']<rival['canonical_name']), (winner,rival)
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':winner['canonical_name']}))
