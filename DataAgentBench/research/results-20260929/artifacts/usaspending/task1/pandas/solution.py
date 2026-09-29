import pandas as pd
import re,json
from pathlib import Path
D=Path('/workspace/data')
c=pd.read_parquet(D/'contracts_db/contracts.parquet')
a=pd.read_parquet(D/'contracts_db/contract_amounts.parquet').drop_duplicates('award_id',keep='first')
al=pd.read_parquet(D/'agencies_db/agency_aliases.parquet').set_index('surface_form').canonical_name
c=c[c.awarding_agency.map(al).eq('Department of Defense')]
x=c.merge(a,on='award_id',how='left',validate='many_to_one')
def classify(s):
 t=s.lower().replace('–','-').replace('‑','-')
 n=re.fullmatch(r'\s*\$?([\d,]+(?:\.\d+)?)\s*([kmb])?\s*(?:usd)?\s*',t)
 if n:return float(n[1].replace(',',''))*{'k':1e3,'m':1e6,'b':1e9,None:1}[n[2]]>1e6
 if re.search(r'(six|five|four|three|two|6|5|4)[ -](?:figure|digit)|thousand|nominal|pocket change|sub-million',t):return False
 if re.search(r'(?:below\b|under\b|shy|less than|without crossing|without reaching|without entering|not a seven|not breaking|seldom reach).{0,45}(?:million|seven.figure)|half.million|half a million',t) and not re.search(r'nine.figure|hundred million',t):return False
 if re.search(r'(seven|eight|nine|ten|7|8|9)[ -]figure|million|billion',t):return True
 if re.search(r'(six|five|four|three|two|6|5|4)[ -]figure|thousand|nominal|pocket change',t):return False
 return None

r=pd.read_parquet(D/'recipients_db/recipients.parquet').set_index('uei')
def numeric(s):
 t=s.lower().replace(',','').replace('$','').replace('usd','').strip()
 m=re.fullmatch(r'(-?[0-9.]+)\s*([kmb])?',t)
 return float(m[1])*{None:1,'k':1e3,'m':1e6,'b':1e9}[m[2]] if m else None
r['total']=r.total_amount_text.map(numeric)
x=x.join(r[['n_contracts','total']],on='recipient_uei')
x['above']=x.amount_text.map(classify)
x['source']='amount wording/numeric'
for i,v in x.iterrows():
 if v.n_contracts==1 or v.total<1e6:
  x.loc[i,'above']=bool(v.total>1e6)
  x.loc[i,'source']='recipient total'

# These annotations interpret prose only: no answer or award count is stored.
review=json.loads(Path('/workspace/work/qualitative_review.json').read_text())
review_map={v['amount_text']:v['above_threshold'] for v in review}
missing=x.above.isna()
x.loc[missing,'above']=x.loc[missing,'amount_text'].map(review_map)
x.loc[missing,'source']='reviewed qualitative wording and related records'
assert x.above.notna().all(), 'Unresolved amounts'
assert x.award_id.notna().all()
assert x.amount_text.notna().all()
# Direct joins fully cover this dataset; no speculative identifier normalization.
answer=int(x.loc[x.above.eq(True),'award_id'].nunique())
x.to_csv('/workspace/work/classification.csv',index=False)
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':f'{answer:,} distinct contract awards.'}))
print(json.dumps({'defense_awards':len(x),'qualifying_distinct_awards':answer,'reviewed_qualitative_records':int(missing.sum())}))
