"""Count DoD awards using Ibis/DuckDB; retain physical amount-file order.
Qualitative_review.json records semantic judgments of otherwise vague prose.
Recipient totals resolve singleton recipients and constrain small portfolios.
"""
from pathlib import Path
import json
import ibis

ROOT=Path('/workspace/data')
OUT=Path('/workspace/work')
con=ibis.duckdb.connect()
contracts=con.read_parquet(str(ROOT/'contracts_db/contracts.parquet'))
aliases=con.read_parquet(str(ROOT/'agencies_db/agency_aliases.parquet'))
recipients=con.read_parquet(str(ROOT/'recipients_db/recipients.parquet'))
# DuckDB exposes the source row number; all selection and joins remain Ibis.
amounts=con.sql("SELECT award_id, amount_text, file_row_number AS source_row FROM read_parquet('/workspace/data/contracts_db/contract_amounts.parquet', file_row_number=true)")
amounts=amounts.mutate(ordinal=ibis.row_number().over(ibis.window(group_by='award_id',order_by='source_row')))
amounts=amounts.filter(amounts.ordinal==0)
assert contracts.anti_join(amounts,'award_id').count().execute()==0
assert contracts.anti_join(aliases,contracts.awarding_agency==aliases.surface_form).count().execute()==0
base=contracts.join(aliases,contracts.awarding_agency==aliases.surface_form).filter(aliases.canonical_name=='Department of Defense').select(contracts)
base=base.join(amounts,'award_id').join(recipients,base.recipient_uei==recipients.uei).select(base.award_id,amounts.amount_text,recipients.n_contracts,recipients.total_amount_text)

def numeric(expr):
    s=expr.lower().strip()
    clean=s.re_replace(r'[$,\s]|usd','').re_replace(r'[kmb]$','')
    multiplier=ibis.cases((s.endswith('k'),1e3),(s.endswith('m'),1e6),(s.endswith('b'),1e9),else_=1.0)
    return clean.try_cast('float64')*multiplier

review=json.loads((OUT/'qualitative_review.json').read_text())
lookup=ibis.memtable({'amount_text':list(review),'reviewed_above':list(review.values())})
base=base.left_join(lookup,'amount_text')
s=base.amount_text.lower()
# Handle explicit negation before positive magnitude expressions.
negative=s.re_search(r'(?:sub[ -]|below |below the |under the |under |less than |shy of (?:the )?|not a |without (?:crossing into|entering) |not dipping into |without reaching )(?:seven[ -]figures?|millions)') | s.re_search(r'not reaching the multi-million|much less than the typical mid-to-high seven|six[ -]figure.*rather than.*multi-million')
pos=s.re_search(r'(seven|eight|nine|ten|7|8|9|10)[ -]figure|billion|millions|multi.million')
neg=s.re_search(r'(four|five|six|4|5|6)[ -]figure|thousand|sub.million|below.*million|under.*million|without.*million|fraction.*million|million.*threshold')
qual=ibis.cases((negative,False),(pos,True),(neg,False),else_=base.reviewed_above)
amount=numeric(base.amount_text)
total=numeric(base.total_amount_text)
# Prefer direct numeric amounts; singleton totals recover the amount for vague prose.
above=ibis.cases((amount.notnull(),amount>1_000_000),((base.n_contracts==1)&total.notnull(),total>1_000_000),(total<=1_000_000,False),else_=qual)
result=base.mutate(above_threshold=above)
assert result.filter(result.above_threshold.isnull()).count().execute()==0
(OUT/'classification_audit.json').write_text(json.dumps(result.select('award_id','amount_text','above_threshold').to_pyarrow().to_pylist(), indent=2))
count=int(result.filter(result.above_threshold).award_id.nunique().execute())
(OUT/'answer.json').write_text(json.dumps({'answer':f'{count:,} distinct contract awards.'})+'\n')
print(count)
