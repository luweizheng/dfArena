import pandas as pd
import re,json
from fractions import Fraction
from pathlib import Path
ROOT=Path('/workspace/data')
def read(p): return pd.read_parquet(ROOT/p)
c=read('contracts_db/contracts.parquet')
a=read('contracts_db/contract_amounts.parquet').drop_duplicates('award_id',keep='first')
alias=read('agencies_db/agency_aliases.parquet').set_index('surface_form').canonical_name
c['agency']=c.awarding_agency.map(alias)
assert c.agency.notna().all()
d=c.merge(a,on='award_id',how='left',validate='many_to_one')
assert d.amount_text.notna().all()
def classify(s):
 t=s.lower().strip()
 m=re.fullmatch(r'\$?\s*([+-]?[\d,]+(?:\.\d+)?)\s*(k|m|b|usd)?',t)
 if m:return float(m[1].replace(',',''))*{'k':1000,'m':1000000,'b':1000000000}.get(m[2],1)>1000000
 if re.search(r'not soaring to the seven.figure|under the million.mark',t):return False
 if re.search(r'(sub.million|(?:four|five|six)[ -]figure|hundred thousand|thousands of dollars)',t): return False
 if re.search(r'((?:seven|eight|nine|ten)[ -](?:figure|digit)|millions|multi.million|mid.million|billion|single.digit million)',t):return True
 if re.search(r'hundreds.of.thousands|hundred.thousand|six digits|triple-digit thousand|half.million|modest|small.scale|minor|pocket.change|small allocation|few thousand|well short of million',t):return False
 if re.search(r'single.digit million',t):return True
 return None
d['high']=d.amount_text.map(classify)
g=d.groupby('agency').agg(n=('award_id','size'),yes=('high',lambda s:s.eq(True).sum()),unknown=('high',lambda s:s.isna().sum()))
g=g[g.n>=10];g['lower']=g.yes/g.n;g['upper']=(g.yes+g.unknown)/g.n
print(g.sort_values('upper',ascending=False).to_string())
d.to_pickle('/workspace/work/classified.pkl')

# Prove the result with bounds, leaving vague descriptions unresolved.
# Even assigning every unresolved competitor award above the threshold
# cannot overtake the winner's confirmed qualifying awards.
ranked=sorted(g.index,key=lambda name:(-Fraction(int(g.loc[name,'yes']),int(g.loc[name,'n'])),name))
winner=ranked[0]
win_lower=Fraction(int(g.loc[winner,'yes']),int(g.loc[winner,'n']))
for name in ranked[1:]:
    upper=Fraction(int(g.loc[name,'yes']+g.loc[name,'unknown']),int(g.loc[name,'n']))
    assert win_lower>upper or (win_lower==upper and winner<name), (name,upper)
g.to_csv('/workspace/work/agency_bounds.csv')
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':winner})+'\n')
print('Winner:',winner)
