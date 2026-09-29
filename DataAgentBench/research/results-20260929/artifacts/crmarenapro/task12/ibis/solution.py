import json
from pathlib import Path
import ibis


def clean_id(col):
    return col.strip().re_replace(r'^#+', '')


def main():
    con = ibis.duckdb.connect()
    root = Path('/workspace/data')
    opportunities = con.read_parquet(str(root / 'sales_pipeline/Opportunity.parquet'))
    contracts = con.read_parquet(str(root / 'sales_pipeline/Contract.parquet'))
    users = con.read_parquet(str(root / 'core_crm/User.parquet'))
    opportunities = opportunities.select(
        agent_id=clean_id(opportunities.OwnerId),
        contract_id=clean_id(opportunities.ContractID__c),
        created_date=opportunities.CreatedDate.strip().cast('timestamp').date(),
    )
    contracts = contracts.select(
        contract_id=clean_id(contracts.Id),
        signed_date=contracts.CompanySignedDate.strip().cast('date'),
    )
    contracts = contracts.filter(
        (contracts.signed_date >= ibis.date('2023-04-01'))
        & (contracts.signed_date < ibis.date('2023-05-01'))
    )
    agents = users.select(agent_id=clean_id(users.Id)).distinct()
    cycles = opportunities.join(contracts, 'contract_id').semi_join(agents, 'agent_id')
    cycles = cycles.mutate(days=cycles.signed_date.delta(cycles.created_date, unit='day'))
    ranking = cycles.group_by('agent_id').aggregate(
        average_days=cycles.days.mean(), opportunity_count=cycles.days.count()
    )
    ranking = ranking.filter(ranking.opportunity_count > 0).order_by('average_days', 'agent_id')
    rows = ranking.to_pyarrow().to_pylist()
    if not rows:
        raise ValueError('No eligible opportunities')
    Path('/workspace/work/ranking.json').write_text(json.dumps(rows, indent=2))
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': rows[0]['agent_id']}))
    print(json.dumps(rows[:5], indent=2))


if __name__ == '__main__':
    main()
