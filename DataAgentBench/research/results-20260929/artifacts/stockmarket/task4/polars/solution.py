import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    info = pl.read_parquet(DATA / 'stockinfo/stockinfo.parquet').filter(
        (pl.col('Listing Exchange') == 'N') & (pl.col('ETF') == 'N')
    )
    rows = []
    for stock in info.iter_rows(named=True):
        symbol = stock['Symbol']
        filename = 'PRN__table' if symbol == 'PRN' else symbol
        prices = pl.scan_parquet(DATA / 'stocktrade' / f'{filename}.parquet')
        counts = prices.filter(pl.col('Date').str.starts_with('2017-')).select(
            (pl.col('Close') > pl.col('Open')).sum().cast(pl.Int64).alias('up_days'),
            (pl.col('Close') < pl.col('Open')).sum().cast(pl.Int64).alias('down_days'),
        ).collect().row(0, named=True)
        rows.append({'symbol': symbol, 'name': stock['Company Description'], **counts})
    ranked = (pl.DataFrame(rows).with_columns(
        (pl.col('up_days') - pl.col('down_days')).alias('difference')
    ).filter(pl.col('difference') > 0)
      .sort(['difference', 'symbol'], descending=[True, False]))
    ranked.write_csv(OUT / 'ranked_stocks.csv')
    top = ranked.head(5)
    print(top.write_json())
    names = top.select(pl.col('name').str.split(' is ').list.first().str.split(' specializes in ').list.first().str.split(' provides ').list.first()).to_series().to_list()
    answer = '; '.join(names)
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()
