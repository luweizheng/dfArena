import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def clean_id(series):
    return series.astype('string').str.strip().str.lstrip('#')

def main():
    opportunities = pd.read_parquet(DATA / 'sales_pipeline/Opportunity.parquet')
    contracts = pd.read_parquet(DATA / 'sales_pipeline/Contract.parquet')
    users = pd.read_parquet(DATA / 'core_crm/User.parquet', columns=['Id'])
    for col in ['Id', 'OwnerId', 'ContractID__c']:
        opportunities[col] = clean_id(opportunities[col])
    contracts['Id'] = clean_id(contracts['Id'])
    users['Id'] = clean_id(users['Id'])
    contracts['signed'] = pd.to_datetime(contracts['CompanySignedDate'].str.strip(), utc=True)
    opportunities['created'] = pd.to_datetime(opportunities['CreatedDate'].str.strip(), utc=True)
    april = contracts.loc[(contracts['signed'] >= '2023-04-01') & (contracts['signed'] < '2023-05-01'), ['Id', 'signed']]
    deals = opportunities.merge(april, left_on='ContractID__c', right_on='Id', how='inner', validate='many_to_one')
    assert deals['OwnerId'].isin(users['Id']).all()
    assert deals['created'].notna().all()
    # Compare calendar dates, as the policy defines days between dates.
    deals['cycle_days'] = (deals['signed'].dt.normalize() - deals['created'].dt.normalize()).dt.days
    averages = deals.groupby('OwnerId')['cycle_days'].agg(['mean', 'count']).sort_values('mean')
    assert len(averages) and (averages['mean'] == averages['mean'].min()).sum() == 1
    averages.to_csv(OUT / 'agent_averages.csv')
    answer = str(averages.index[0])
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
    print(averages.to_string())
    print(json.dumps({'answer': answer}))

if __name__ == '__main__':
    main()
