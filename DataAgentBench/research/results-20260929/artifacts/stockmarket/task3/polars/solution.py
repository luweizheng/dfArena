from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

# Include every status indicating deficiency or delinquency, including
# combinations with bankruptcy. Listing Exchange Q identifies NASDAQ listings.
companies = pl.read_parquet(DATA / 'stockinfo/stockinfo.parquet').filter(
    (pl.col('Listing Exchange') == 'Q')
    & pl.col('Financial Status').is_in(['D', 'E', 'G', 'H', 'J', 'K'])
)
results = []
for company in companies.iter_rows(named=True):
    symbol = company['Symbol']
    filename = 'PRN__table' if symbol == 'PRN' else symbol
    stats = (
        pl.scan_parquet(DATA / 'stocktrade' / f'{filename}.parquet')
        .filter(pl.col('Date').str.starts_with('2008-'))
        .select(
            pl.col('Volume').count().alias('non_null_days'),
            pl.col('Volume').mean().alias('average_daily_volume'),
        ).collect().row(0, named=True)
    )
    if stats['non_null_days'] > 0:
        results.append({
            'symbol': symbol,
            'description': company['Company Description'],
            'financial_status': company['Financial Status'],
            **stats,
        })

# The source has descriptive sentences rather than a separate company-name field.
# Extract their leading company names, retaining the source spelling.
result = pl.DataFrame(results).with_columns(
    pl.col('description').str.split(' specializes in').list.first()
    .str.split(', based in').list.first()
    .str.split(' provides ').list.first()
    .str.split(' is at ').list.first()
    .str.split(' harnesses ').list.first()
    .str.split(' is dedicated ').list.first()
    .alias('company_name')
).sort('company_name')
result.write_csv(OUT / 'computed_volumes.csv')
entries = [
    f"{r['company_name']} ({r['symbol']}): {r['average_daily_volume']:,.6f}" 
    for r in result.iter_rows(named=True)
]
answer = 'Average daily trading volume in 2008 (shares/day; non-null observations only): ' + '; '.join(entries) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(answer)

if __name__ == '__main__':
    assert result.height > 0
    assert result['average_daily_volume'].null_count() == 0
