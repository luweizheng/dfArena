import polars as pl
import json
from pathlib import Path
ROOT=Path('/workspace/data')
c=pl.read_parquet(ROOT/'contracts_db/contracts.parquet')
a=pl.read_parquet(ROOT/'contracts_db/contract_amounts.parquet').unique('award_id',keep='first',maintain_order=True)
s=pl.read_parquet(ROOT/'agencies_db/naics_sectors.parquet')
d=c.join(a,on='award_id',how='left',validate='1:1').with_columns(pl.col('naics_code').str.replace(r'(?i)^naics[-: ]*','').str.replace_all('-','').alias('clean_code'))
assert d.height==c.height and d['amount_text'].null_count()==0
assert d.filter(~pl.col('clean_code').str.contains(r'^\d{6}$')).height==0
d=d.with_columns(pl.col('clean_code').str.slice(0,2).alias('sector'),pl.col('amount_text').str.to_lowercase().alias('txt'))
d=d.with_columns(pl.col('txt').str.replace_all(r'[$,\s]','').str.replace(r'usd$','').cast(pl.Float64,strict=False).alias('numeric'))
d=d.with_columns(((pl.col('numeric')>=10000000).fill_null(False)|pl.col('txt').str.contains(r'eight.figure|nine.figure|ten.figure|tens of millions|hundreds of millions|\bbillion')).alias('qualifies'))
represented=d.filter('qualifies').select('sector').unique().join(s,on='sector',how='inner').select('sector').unique().sort('sector')

# A recipient whose awards all belong to one sector can establish that sector
# by the pigeonhole principle, even when individual amounts are qualitative.
def money_expr(column):
    cleaned = pl.col(column).str.to_lowercase().str.replace_all(r"[$,\s]", "").str.replace(r"usd$", "")
    value = cleaned.str.replace(r"[kmb]$", "").cast(pl.Float64, strict=False)
    multiplier = (pl.when(cleaned.str.ends_with("k")).then(1e3)
                  .when(cleaned.str.ends_with("m")).then(1e6)
                  .when(cleaned.str.ends_with("b")).then(1e9).otherwise(1.0))
    return value * multiplier
r = pl.read_parquet(ROOT / 'recipients_db/recipients.parquet').with_columns(money_expr('total_amount_text').alias('total'))
groups = d.group_by('recipient_uei').agg(pl.len().alias('observed_n'), pl.col('sector').n_unique().alias('sector_count'), pl.col('sector').first())
inferred = groups.join(r, left_on='recipient_uei', right_on='uei').filter(
    (pl.col('sector_count') == 1) & (pl.col('observed_n') == pl.col('n_contracts')) &
    (pl.col('total') >= pl.col('n_contracts') * 10000000)
).select('sector')
numeric_sectors = d.with_columns(money_expr('amount_text').alias('parsed_amount')).filter(pl.col('parsed_amount') >= 10000000).select('sector')
represented = pl.concat([represented, inferred, numeric_sectors]).unique().sort('sector')
assert represented.join(s, on='sector', how='anti').is_empty()
represented.write_json('/workspace/work/represented_sectors.json')
print(represented['sector'].to_list())
Path('/workspace/work/answer.json').write_text(json.dumps({'answer':str(represented.height)}))
