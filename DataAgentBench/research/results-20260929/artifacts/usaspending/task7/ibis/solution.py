import ibis
import json
from pathlib import Path
con = ibis.duckdb.connect()
c = con.read_parquet('/workspace/data/contracts_db/contracts.parquet')
# DuckDB ordinality captures physical file order before any relational operations.
a = con.sql("SELECT *, ordinality AS source_row FROM read_parquet('/workspace/data/contracts_db/contract_amounts.parquet') WITH ORDINALITY")
a = a.mutate(rn=ibis.row_number().over(ibis.window(group_by=a.award_id, order_by=a.source_row))).filter(lambda t:t.rn==0)
assert c.anti_join(a,'award_id').count().execute() == 0

c=c.mutate(sector=c.naics_code.lower().re_replace('^naics[- :]*','').upper().translate('OISZGB','015268').re_replace('[^0-9]','').substr(0,2))
r=con.read_parquet('/workspace/data/recipients_db/recipients.parquet')
rs=r.total_amount_text.lower().re_replace('[$, ]','').re_replace('usd$','')
rv=rs.re_extract(r'^(-?[0-9]+(?:\.[0-9]+)?)[kmb]?$',1).try_cast('float64')*ibis.cases((rs.endswith('k'),1000),(rs.endswith('m'),1000000),(rs.endswith('b'),1000000000),else_=1)
r=r.mutate(total=rv)
t=c.join(a,'award_id').join(r,c.recipient_uei==r.uei).select(c.award_id,c.sector,a.amount_text,c.recipient_uei,r.total,r.n_contracts)

s=t.amount_text.lower()
numeric=s.re_replace('[$, ]','').re_replace('usd$','')
value=numeric.re_extract(r'^(-?[0-9]+(?:\.[0-9]+)?)[kmb]?$',1).try_cast('float64')
value=value*ibis.cases((numeric.endswith('k'),1000),(numeric.endswith('m'),1000000),(numeric.endswith('b'),1000000000),else_=1)
high=s.re_search(r'(eight|nine|ten|eleven|[89]|10)[ -]figure|tens[ -]of[ -]millions|hundreds[ -]of[ -]millions|billion|hundred million|upper echelons of large-scale construction budgets')
low=s.re_search(r'(four|five|six|seven)[ -]figure|thousand|sub-million|single[ -]digit million|low.to.mid millions|millions range|million-dollar spectrum|millions spectrum|six[ -]digit|five[ -]digit|six digits|non-million|rounding error|modest|minor|small|routine|petty|low.{0,15}million|lower.{0,15}million|million.{0,15}lower|mid.{0,10}million|million.{0,10}mid|several million|half.million|below.{0,20}million|short of.{0,20}million|under.{0,20}million|barely|minimal|token|initial|entry.level|pocket|preliminary')
t=t.mutate(status=ibis.cases((value.notnull(),ibis.ifelse(value>=10000000,'yes','no')),(t.total<10000000,'no'),((t.n_contracts==1)&(t.total>=10000000),'yes'),(high,'yes'),(low,'no'),else_='unknown'))
# Bound individual amounts by magnitude and the recipient's supplied total.
textcol=t.amount_text.lower()
upper=ibis.cases((textcol.re_search(r'five[ -](figure|digit)'),100000),
 (textcol.re_search(r'six[ -](figure|digit)|six digits|hundreds of thousands'),1000000),
 (textcol.re_search(r'seven[ -](figure|digit)'),10000000),
 (t.status=='no',10000000),(textcol.re_search(r'eight[ -]figure'),100000000),else_=t.total)
t=t.mutate(lo=ibis.ifelse(t.status=='yes',10000000.0,0.0),hi=upper)
for _ in range(3):
 bounds=t.group_by('recipient_uei').aggregate(sum_lo=t.lo.sum(),sum_hi=t.hi.sum())
 joined=t.join(bounds,'recipient_uei')
 t=joined.mutate(lo=ibis.greatest(joined.lo,joined.total-50000-(joined.sum_hi-joined.hi)),hi=ibis.least(joined.hi,joined.total+50000-(joined.sum_lo-joined.lo))).drop('sum_lo','sum_hi')
 t=t.mutate(status=ibis.cases((t.lo>=10000000,'yes'),(t.hi<10000000,'no'),else_=t.status))
groups=t.group_by('sector','recipient_uei').aggregate(
 yes=(t.status=='yes').sum(), unknown=(t.status=='unknown').sum(),
 total=t.total.max(), committed=ibis.ifelse(t.status=='unknown',0,t.lo).sum())
groups=groups.mutate(possible=ibis.least(groups.unknown,ibis.greatest(0,((groups.total+50000-groups.committed)/10000000).floor())))
stats=groups.group_by('sector').aggregate(yes=groups.yes.sum(),unknown=groups.possible.sum()).order_by(ibis.desc('yes'),'sector')
rows=stats.to_pyarrow().to_pylist()
print(rows)
Path('/workspace/work/unknown.json').write_text(json.dumps(t.filter(t.status=='unknown').to_pyarrow().to_pylist(),indent=2))
Path('/workspace/work/counts.json').write_text(json.dumps(rows,indent=2))
if all((rows[0]['yes']>r['yes']+r['unknown'] or (rows[0]['yes']==r['yes']+r['unknown'] and rows[0]['sector']<r['sector'])) for r in rows[1:]):
 Path('/workspace/work/answer.json').write_text(json.dumps({'answer':rows[0]['sector']}))
else:
 raise RuntimeError('Unresolved sector ranking')
