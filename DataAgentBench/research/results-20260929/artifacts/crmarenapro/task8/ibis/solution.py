import json
from pathlib import Path
import ibis


def clean(expr):
    return expr.strip().re_replace(r'^#+', '')


def main():
    con = ibis.duckdb.connect()
    history = con.read_parquet('/workspace/data/support/casehistory__c.parquet')
    users = con.read_parquet('/workspace/data/core_crm/User.parquet')
    cases = con.read_parquet('/workspace/data/support/Case.parquet')
    # LAST_N_QUARTERS: the four complete calendar quarters before today.
    end = ibis.date('2023-04-10').truncate('Q')
    start = end - ibis.interval(years=1)
    assignments = history.filter(history.field__c.strip() == 'Owner Assignment').select(
        case_id=clean(history.caseid__c),
        source=clean(history.oldvalue__c),
        destination=clean(history.newvalue__c),
        event_date=history.createddate.cast('timestamp').date(),
    )
    period = assignments.filter(
        (assignments.event_date >= start) & (assignments.event_date < end)
    )
    valid_cases = cases.select(case_id=clean(cases.id)).distinct()
    period = period.semi_join(valid_cases, 'case_id')
    transfers = period.filter(
        period.source.notnull() & (period.source != '')
        & period.destination.notnull() & (period.destination != '')
        & (period.source != period.destination)
    )
    # Both initial recipients and transfer recipients handle cases; outgoing
    # owners also handled the case they transferred during the period.
    handled = period.select(agent=period.destination, case_id=period.case_id).union(
        transfers.select(agent=transfers.source, case_id=transfers.case_id)
    ).group_by('agent').aggregate(cases_handled=ibis._.case_id.nunique())
    counts = transfers.group_by(agent=transfers.source).aggregate(transfer_count=transfers.count())
    agents = users.select(agent=clean(users.Id)).distinct()
    ranked = counts.join(handled, 'agent').semi_join(agents, 'agent')
    ranked = ranked.filter((ranked.cases_handled > 0) & (ranked.transfer_count > 0))
    result = ranked.order_by('transfer_count', 'agent').limit(1).to_pyarrow().to_pylist()
    if not result:
        raise ValueError('No eligible agent')
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': result[0]['agent']}))


if __name__ == '__main__':
    main()
