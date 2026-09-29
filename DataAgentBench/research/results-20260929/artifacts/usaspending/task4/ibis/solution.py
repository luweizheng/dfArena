import ibis, json
from pathlib import Path
con=ibis.duckdb.connect()
c=con.read_parquet('/workspace/data/contracts_db/contracts.parquet')
# DuckDB's file_row_number preserves the supplied Parquet record order.
m=con.sql("SELECT *, file_row_number AS original_row FROM read_parquet('/workspace/data/contracts_db/contract_amounts.parquet', file_row_number=true)")
m=m.mutate(rn=ibis.row_number().over(ibis.window(group_by='award_id',order_by='original_row'))).filter(lambda t:t.rn==0)
a=con.read_parquet('/workspace/data/agencies_db/agency_aliases.parquet')
print('unmatched amounts',c.anti_join(m,'award_id').count().execute())
t=c.left_join(m,'award_id').left_join(a,c.awarding_agency==a.surface_form).select(c.award_id,m.amount_text,agency=a.canonical_name)
s=t.amount_text.lower()
clean=s.re_replace(r'[$,\s]|usd','')
num=clean.re_replace('[kmb]$','').try_cast('float64') * ibis.cases((clean.endswith('k'),1000),(clean.endswith('m'),1000000),(clean.endswith('b'),1000000000),else_=1)
hi=s.re_search(r'(seven|eight|nine|ten|eleven)[ -]figure|millions|billion|\bmillion[ -]dollar|\bmillion range|multi[ -]?million|several million|single-digit million|(seven|eight|nine|ten)[ -]digit')
lo=s.re_search(r'(three|four|five|six)[ -]figure|thousands|sub[ -]million|below.{0,15}million|under.{0,15}million|hundred thousand')
t=t.mutate(high=ibis.cases((num.notnull(),num>1000000),(lo,False),(hi,True),(s.re_search(r'modest|minor|small|micro-scale|petty cash|pocket change|minimal|barely|economical|entry-level|routine monthly'),False),else_=ibis.null().cast('boolean')))
g=t.group_by('agency').aggregate(n=t.count(),high=t.high.sum(),unknown=t.high.isnull().sum()).filter(lambda x:x.n>=10)
g=g.mutate(lower=g.high/g.n,upper=(g.high+g.unknown)/g.n).order_by(ibis.desc('lower'),'agency')
print(g.to_pyarrow().to_pylist())
t.to_parquet('/workspace/work/classified.parquet')

# The result need not depend on assigning amounts to every vague description.
# Prove the winner even if all unresolved competitor amounts exceed the threshold
# and all unresolved winner amounts do not. Cross multiplication avoids rounding.
assert c.anti_join(m, 'award_id').count().execute() == 0
assert t.agency.isnull().sum().execute() == 0
assert t.count().execute() == c.count().execute()
rows = g.to_pyarrow().to_pylist()
winner = rows[0]
for other in rows[1:]:
    lhs = winner['high'] * other['n']
    rhs = (other['high'] + other['unknown']) * winner['n']
    assert lhs > rhs or (lhs == rhs and winner['agency'] < other['agency']), (winner, other)
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': winner['agency']}) + '\n')
Path('/workspace/work/proportion_bounds.json').write_text(json.dumps(rows, indent=2) + '\n')
