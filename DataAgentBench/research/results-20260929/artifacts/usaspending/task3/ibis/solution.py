import json
from pathlib import Path
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work/answer.json')


def main():
    backend = ibis.duckdb.connect()
    contracts = backend.read_parquet(str(DATA / 'contracts_db/contracts.parquet'))
    sectors = backend.read_parquet(str(DATA / 'agencies_db/naics_sectors.parquet'))

    # These are the observed formats; fail if additional normalization is needed.
    invalid = contracts.filter(
        ~contracts.naics_code.re_search(r'^(\d{6}|\d{2}-\d{4}|naics-\d{6})$')
        | ~contracts.recipient_uei.re_search(
            r'^([A-Z0-9]{12}|uei:[a-z0-9]{12}|[a-z0-9]{12}-uei)$'
        )
    )
    assert invalid.count().execute() == 0
    normalized = contracts.select(
        naics=contracts.naics_code.upper().re_replace('^NAICS-', '').re_replace('-', ''),
        uei=contracts.recipient_uei.upper().re_replace('^UEI:', '').re_replace('-UEI$', ''),
    )
    target_sectors = sectors.filter(sectors.sector == '33')
    matching = normalized.semi_join(
        target_sectors, normalized.naics.substr(0, 2) == target_sectors.code
    )
    count = int(matching.uei.nunique().execute())
    OUT.write_text(json.dumps({'answer': str(count)}) + '\n')
    print(OUT.read_text(), end='')


if __name__ == '__main__':
    main()
