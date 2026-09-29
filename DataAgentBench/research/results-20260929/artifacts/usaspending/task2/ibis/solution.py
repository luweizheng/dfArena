import ibis
import json
from pathlib import Path
con=ibis.duckdb.connect()
c=con.read_parquet('/workspace/data/contracts_db/contracts.parquet')
r=con.read_parquet('/workspace/data/recipients_db/recipients.parquet')
# DuckDB file_row_number preserves the physical order for conflicting amounts.
a=con.sql("SELECT * FROM read_parquet('/workspace/data/contracts_db/contract_amounts.parquet', file_row_number=true)")
a=a.mutate(rn=ibis.row_number().over(ibis.window(group_by=a.award_id,order_by=a.file_row_number)))
a=a.filter(a.rn==0)
print('unmatched recipients',c.anti_join(r,c.recipient_uei==r.uei).count().execute())
print('unmatched amounts',c.anti_join(a,c.award_id==a.award_id).count().execute())
j=c.join(r,c.recipient_uei==r.uei).join(a,c.award_id==a.award_id)
j=j.filter(j.state.lower().isin(['ca','california','calif.','calif']))
print('CA awards',j.count().execute())
Path('/workspace/work/ca_records.json').write_text(json.dumps(j.select('award_id','recipient_uei','name','n_contracts','total_amount_text','amount_text').to_pyarrow().to_pylist(),indent=2))
# Parse the dataset's numeric currency formats with lazy string expressions.
def money(x):
    clean=x.upper().re_replace(r'USD|[$,\s]','')
    return clean.re_replace('[KMB]$','').try_cast('float64') * ibis.cases((clean.endswith('K'),1e3),(clean.endswith('M'),1e6),(clean.endswith('B'),1e9),else_=1)
t=j.amount_text.lower()
small=t.re_search(r'(?:four|five|six)[- ](?:figure|digit)|hundred[s]?(?:[- ]of)?[- ]thousand|sub[- ]million|under.*million|without breaching the million|not.*seven-figure|high thousands')
large=t.re_search(r'(?:seven|eight|nine|ten)[- ]figure|million|billion')
j=j.mutate(numeric=money(j.amount_text),total_numeric=money(j.total_amount_text))
j=j.mutate(qualifies=ibis.cases((j.numeric.notnull(),j.numeric>1e6),(j.n_contracts==1,j.total_numeric>1e6),(j.total_numeric<=1e6,False),(small,False),(t.contains("below the seven-figure threshold"),False),(large,True),else_=ibis.null().cast('boolean')))

# Resolve remaining prose using its monetary meaning and related recipient records.
# Northrop's other award is seven figures against a $177m total; Cynergy's
# other two awards are tiny against a $27m total. Spectrum's $5.7m total,
# three six-figure awards, tiny supply award, and lower-tier million-dollar
# award indicate a substantial institutional healthcare commitment here.
substantial=t.re_search(r"substantial investment typical of large-scale engineering|mid-tier market expansion investment|standard-tier investment typical for institutional healthcare")
modest=t.re_search(r"minor operational support|pocket change|modest enough|barely makes a ripple|minor adjustments|minor service retainer|annual supply budget|exploratory groundwork|modestly priced software subscription|petty cash|modest budget segment|entry-level commitment|niche software license fee")
j=j.mutate(qualifies=ibis.cases((j.qualifies.notnull(),j.qualifies),(substantial,True),(modest,False),else_=ibis.null().cast('boolean')))
assert j.filter(j.qualifies.isnull()).count().execute()==0
assert c.anti_join(r,c.recipient_uei==r.uei).count().execute()==0
assert c.anti_join(a,c.award_id==a.award_id).count().execute()==0
assert j.count().execute()==j.award_id.nunique().execute()
count=int(j.filter(j.qualifies).count().execute())
Path('/workspace/work/classification_audit.json').write_text(json.dumps(j.select('award_id','amount_text','total_amount_text','n_contracts','qualifies').order_by('award_id').to_pyarrow().to_pylist(),indent=2))
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':f'{count} contract awards.'}))
print(count)
