import json,re
from pathlib import Path
import polars as pl
ROOT=Path('/workspace/data')
def numeric(t):
 t=t.strip().replace(',','').replace('$','').replace(' USD','')
 m=re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*([KMB])?',t,re.I)
 return float(m[1])*{'':1,'K':1e3,'M':1e6,'B':1e9}[(m[2] or '').upper()] if m else None
def classify(t):
 n=numeric(t)
 if n is not None:return int(n>=1e7)
 t=t.lower()
 if re.search(r'(eight|nine|ten|eleven)[ -]figure|tens[ -]of[ -]millions|hundreds[ -]of[ -]millions|billion',t):return 1
 if re.search(r'(four|five|six|seven)[ -]figure|thousand|low.to.mid millions|single.digit million|sub.million|below.*million|without.*million|few million|several million|lower end of the million',t):return 0
 if re.search(r'low.to.mid million|low millions|lower millions|mid.tier millions|mid.level millions|lower range of millions|non.million|six digits|five.digit|barely|rounding error|minor |modest |small.scale|small.budget|small professional seminar|token|trifling|trivial|minimalist|single high.end server|typical administrative overhead',t):return 0
 return None
c=pl.read_parquet(ROOT/'contracts_db/contracts.parquet')
a=pl.read_parquet(ROOT/'contracts_db/contract_amounts.parquet').unique('award_id',keep='first',maintain_order=True)
d=c.join(a,on='award_id',how='left',validate='m:1').with_columns(pl.col('amount_text').map_elements(classify,return_dtype=pl.Int64).alias('qualifies'),pl.col('naics_code').str.replace('(?i)^naics-','').str.replace_all('-','').str.slice(0,2).alias('sector'))
def uei(t):return re.sub(r'[^A-Z0-9]','',re.sub(r'(?i)^uei:|-uei$','',t).upper())
r=pl.read_parquet(ROOT/'recipients_db/recipients.parquet').with_columns(pl.col('uei').map_elements(uei).alias('key'),pl.col('total_amount_text').map_elements(numeric,return_dtype=pl.Float64).alias('total'))
d=d.with_columns(pl.col('recipient_uei').map_elements(uei).alias('key')).join(r.select('key','total'),on='key',how='left',validate='m:1').with_columns(pl.when(pl.col('qualifies').is_null() & (pl.col('total')<1e7)).then(0).otherwise(pl.col('qualifies')).alias('qualifies'))
d=d.join(d.group_by('key').len().rename({'len':'recipient_rows'}),on='key').with_columns(pl.when(pl.col('qualifies').is_null() & (pl.col('recipient_rows')==1) & pl.col('total').is_not_null()).then((pl.col('total')>=1e7).cast(pl.Int64)).otherwise(pl.col('qualifies')).alias('qualifies'))
d.filter(pl.col('qualifies').is_null()).select('award_id','sector','amount_text','total').write_csv('/workspace/work/unresolved.csv')
counts=d.group_by('sector').agg((pl.col('qualifies')==1).sum().alias('certain'),pl.col('qualifies').is_null().sum().alias('uncertain')).sort(['certain','sector'],descending=[True,False])
print(counts)
counts.write_csv('/workspace/work/sector_bounds.csv')
# Propagate recipient totals through conservative monetary intervals. Exact
# recovery is unnecessary; only intervals lying wholly above/below $10M matter.
def interval(t):
 n=numeric(t)
 if n is not None:
  m=re.search(r'([KMB])$',t,re.I)
  tol=0.05*{'K':1e3,'M':1e6,'B':1e9}[m[1].upper()] if m else 1
  return {'lo':max(0.,n-tol),'hi':n+tol}
 text=t.lower()
 for word,power in [('four',3),('five',4),('six',5),('seven',6),('eight',7),('nine',8),('ten',9)]:
  if re.search(word+r'[ -]figure',text):return {'lo':10.**power,'hi':10.**(power+1)}
 q=classify(t)
 return {'lo':1e7 if q==1 else 0.,'hi':1e7 if q==0 else float('inf')}
d=d.with_columns(pl.col('amount_text').map_elements(interval,return_dtype=pl.Struct({'lo':pl.Float64,'hi':pl.Float64})).alias('bounds')).unnest('bounds')
# For each award, subtract the possible amounts of all its recipient's other awards.
d=d.with_columns(pl.col('lo').sum().over('key').alias('sum_lo'),pl.when(pl.col('hi').is_finite()).then(pl.col('hi')).otherwise(0).sum().over('key').alias('sum_hi'),pl.col('hi').is_infinite().sum().over('key').alias('infinite'))
d=d.with_columns((pl.col('total')-(pl.col('sum_lo')-pl.col('lo'))+100000).alias('residual_hi'),pl.when(pl.col('infinite')-pl.col('hi').is_infinite().cast(pl.UInt32)==0).then(pl.col('total')-pl.col('sum_hi')+pl.when(pl.col('hi').is_finite()).then(pl.col('hi')).otherwise(0)-100000).otherwise(float('-inf')).alias('residual_lo'))
resolved=d.with_columns(pl.when(pl.col('qualifies').is_not_null()).then(pl.col('qualifies')).when(pl.col('residual_lo')>=1e7).then(1).when(pl.col('residual_hi')<1e7).then(0).otherwise(None).alias('qualifies'))
counts=resolved.group_by('sector').agg((pl.col('qualifies')==1).sum().alias('certain'),pl.col('qualifies').is_null().sum().alias('uncertain')).sort(['certain','sector'],descending=[True,False])
print(counts)
counts.write_csv('/workspace/work/sector_bounds.csv')
resolved.filter(pl.col('qualifies').is_null()).select('award_id','sector','amount_text','total').write_csv('/workspace/work/unresolved.csv')
# Recipient totals also bound the number of qualifying awards jointly, even
# when no individual ambiguous award can be classified.
per_recipient=resolved.group_by('key','sector').agg((pl.col('qualifies')==1).sum().alias('certain'),pl.col('qualifies').is_null().sum().alias('unknown'),pl.col('total').first(),pl.len().alias('n'))
whole=resolved.group_by('key').agg((pl.col('qualifies')==1).sum().alias('all_certain'),pl.col('sector').n_unique().alias('sectors'))
per_recipient=per_recipient.join(whole,on='key').with_columns(pl.when(pl.col('total').is_not_null()).then(((pl.col('total')+100000)/1e7).floor()-pl.col('all_certain')).otherwise(pl.col('unknown')).clip(lower_bound=0).alias('remaining_capacity'))
per_recipient=per_recipient.with_columns((pl.col('certain')+pl.min_horizontal('unknown','remaining_capacity')).alias('upper'),pl.when((pl.col('certain')==0)&(pl.col('sectors')==1)&(pl.col('total')-100000>=pl.col('n')*1e7)).then(1).otherwise(pl.col('certain')).alias('lower'))
bounds=per_recipient.group_by('sector').agg(pl.col('lower').sum(),pl.col('upper').sum()).sort(['lower','sector'],descending=[True,False])
print(bounds)
bounds.write_csv('/workspace/work/sector_bounds.csv')
winner=bounds.row(0,named=True)
for other in bounds.iter_rows(named=True):
 if other['sector']==winner['sector']:continue
 assert winner['lower']>other['upper'] or (winner['lower']==other['upper'] and winner['sector']<other['sector']), 'Insufficient bounds to determine winner'
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':winner['sector']}))
