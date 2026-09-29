import json,re
from pathlib import Path
import pandas as pd
ROOT=Path('/workspace/data')
c=pd.read_parquet(ROOT/'contracts_db/contracts.parquet')
a=pd.read_parquet(ROOT/'contracts_db/contract_amounts.parquet').drop_duplicates('award_id',keep='first')
s=pd.read_parquet(ROOT/'agencies_db/naics_sectors.parquet')
d=c.merge(a,on='award_id',how='left',validate='many_to_one')
assert d.amount_text.notna().all()
n=d.naics_code.str.lower().str.replace(r'^naics[-: ]*','',regex=True).str.replace('-','',regex=False)
assert n.str.fullmatch(r'\d{6}').all()
d['sector']=n.str[:2].map(s.set_index('code').sector)
assert d.sector.notna().all()
def classify(text):
 t=text.lower().strip().replace('–','-').replace('—','-')
 t=re.sub(r'(?<=\w)-(?=\w)',' ',t)
 numeric=re.fullmatch(r'\$?(-?[\d,]+(?:\.\d+)?)\s*([kmb])?\s*(?:usd)?',t)
 if numeric:
  value=float(numeric[1].replace(',',''))*{'k':1e3,'m':1e6,'b':1e9,None:1}[numeric[2]]
  return int(value>=10000000)
 if re.search(r'\b(eight|nine|ten|eleven)[ -]figures?\b|\btens of millions\b|\bhundreds of millions\b|\bbillion',t): return 1
 if re.search(r'\b(four|five|six|seven)[ -]figures?\b|\bthousands\b|low to mid millions|sub million|without breaching the million|without stretching into the million',t):return 0
 if re.search(r'single digit million|hundred thousand|hundred.thousand|six digit|five digit|low (?:to mid )?millions?|lower (?:ensemble|sweep|spectrum).*million|mid (?:tier |level )?millions?|non million|modest|minor|barely|rounding error|trivial|trifling|single high end server|small professional seminar|small scale|small consulting fee|token sums|minimalist',t): return 0
 return None
d['qualifies']=d.amount_text.map(classify)
# Recipient totals bound individual nonnegative awards and identify single-award amounts.
r=pd.read_parquet(ROOT/'recipients_db/recipients.parquet')
def uei_key(v):
 return re.sub(r'[^a-z0-9]','',re.sub(r'^uei[: -]*|[- :]*uei$','',v.lower()))
r['key']=r.uei.map(uei_key)
assert not r.key.duplicated().any()
d['key']=d.recipient_uei.map(uei_key)
d=d.merge(r[['key','n_contracts','total_amount_text']],on='key',how='left',validate='many_to_one')
assert d.total_amount_text.notna().all()
total_status=d.total_amount_text.map(classify)
d.loc[total_status.eq(0) | d.n_contracts.eq(1), 'qualifies']=total_status
def numeric_interval(text):
 m=re.fullmatch(r'\$?(-?[\d,]+(?:\.\d+)?)\s*([KMBkmb])?\s*(?:USD)?',text.strip())
 assert m, text
 scale={None:1,'k':1e3,'m':1e6,'b':1e9}[m[2].lower() if m[2] else None]
 value=float(m[1].replace(',',''))*scale
 # Abbreviated totals are rounded; retain a conservative rounding interval.
 error=0.5*scale/(10**len(m[1].split('.')[1])) if m[2] and '.' in m[1] else (scale/2 if m[2] else 0)
 return value-error,value+error
# Compute joint bounds within recipient/sector groups, preserving uncertainty.
rows=[]
for (key,sector),g in d.groupby(['key','sector']):
 lo=int(g.qualifies.eq(1).sum()); hi=lo+int(g.qualifies.isna().sum())
 total_lo,total_hi=numeric_interval(g.total_amount_text.iloc[0])
 hi=min(hi,int(total_hi//10000000))
 if len(g)==g.n_contracts.iloc[0] and lo==0 and total_lo>=len(g)*10000000:
  lo=1
 rows.append((sector,lo,hi))
bounds=pd.DataFrame(rows,columns=['sector','lower','upper']).groupby('sector').sum()
bounds['unknown']=bounds.upper-bounds.lower
bounds=bounds.sort_values(['lower','sector'],ascending=[False,True])
print(bounds.to_string())
bounds.to_csv('/workspace/work/count_bounds.csv')
d[d.qualifies.isna()].to_csv('/workspace/work/unresolved.csv',index=False)
winner=bounds.index[0]
# A conservative proof suffices even where descriptions do not give an exact amount.
assert all(bounds.loc[winner,'lower']>row.upper or (bounds.loc[winner,'lower']==row.upper and int(winner)<int(code)) for code,row in bounds.iterrows() if code!=winner), 'Need to resolve more qualitative amounts'
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':winner})+'\n')
