import json
from pathlib import Path
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')


def main():
    backend = ibis.duckdb.connect()
    contracts = backend.read_parquet(str(DATA / 'contracts_db/contracts.parquet'))
    amounts = backend.read_parquet(str(DATA / 'contracts_db/contract_amounts.parquet'))
    recipients = backend.read_parquet(str(DATA / 'recipients_db/recipients.parquet'))

    # Actual identifiers match directly; no lossy normalization is needed.
    assert amounts.anti_join(contracts, 'award_id').count().execute() == 0
    assert contracts.anti_join(
        recipients, contracts.recipient_uei == recipients.uei
    ).count().execute() == 0
    assert contracts.award_id.nunique().execute() == contracts.count().execute()

    # Keep distinct UEIs separate, including those belonging to the same company.
    ranked = contracts.group_by('recipient_uei').aggregate(total_contracts=ibis._.count())
    checked = ranked.join(recipients, ranked.recipient_uei == recipients.uei)
    assert checked.filter(checked.total_contracts != checked.n_contracts).count().execute() == 0
    top_ten = ranked.order_by(ibis.desc('total_contracts'), 'recipient_uei').limit(10)

    # The first amount record is authoritative; any later record is superseded.
    # Existence of a later row depends only on the record count, not its amount.
    superseded = (
        amounts.group_by('award_id')
        .aggregate(amount_records=ibis._.count())
        .filter(ibis._.amount_records > 1)
    )
    selected = contracts.semi_join(top_ten, 'recipient_uei')
    result = int(selected.semi_join(superseded, 'award_id').count().execute())
    (OUT / 'answer.json').write_text(json.dumps({'answer': f'{result} contracts.'}) + '\n')
    print((OUT / 'answer.json').read_text(), end='')


if __name__ == '__main__':
    main()
