import json
from datetime import date
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def clean_id(name):
    return pl.col(name).str.strip_chars().str.strip_chars_start('#')

opportunities = pl.read_parquet(DATA / 'sales_pipeline/Opportunity.parquet').select(
    clean_id('Id').alias('OpportunityId'),
    clean_id('ContractID__c').alias('ContractId'),
    clean_id('OwnerId').alias('AgentId'),
    pl.col('CreatedDate').str.strip_chars().str.slice(0, 10).str.to_date('%Y-%m-%d').alias('CreatedDate'),
)
contracts = pl.read_parquet(DATA / 'sales_pipeline/Contract.parquet').select(
    clean_id('Id').alias('ContractId'),
    pl.col('CompanySignedDate').str.strip_chars().str.to_date('%Y-%m-%d').alias('SignedDate'),
)
users = pl.read_parquet(DATA / 'core_crm/User.parquet').select(clean_id('Id').alias('AgentId')).unique()
april = contracts.filter(
    (pl.col('SignedDate') >= date(2023, 4, 1)) & (pl.col('SignedDate') < date(2023, 5, 1))
)
cycles = opportunities.join(april, on='ContractId', how='inner', validate='m:1').join(users, on='AgentId', how='semi').with_columns(
    (pl.col('SignedDate') - pl.col('CreatedDate')).dt.total_days().alias('CycleDays')
)
assert cycles.height > 0
assert cycles['CycleDays'].null_count() == 0
ranking = cycles.group_by('AgentId').agg(
    pl.col('CycleDays').mean().alias('AverageDays'),
    pl.len().alias('Opportunities'),
).sort(['AverageDays', 'AgentId'])
ranking.write_csv(OUT / 'agent_average_cycles.csv')
assert ranking.filter(pl.col('AverageDays') == ranking['AverageDays'][0]).height == 1
answer = ranking['AgentId'][0]
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(ranking.head(5))
print(answer)
