import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    info = con.read_parquet('/workspace/data/stockinfo/stockinfo.parquet')
    etfs = info.filter(
        (info['Listing Exchange'] == 'P') & (info['ETF'] == 'Y')
    ).select('Symbol').distinct()
    prices = con.read_parquet(
        '/workspace/data/stocktrade/*.parquet',
        filename=True,
        union_by_name=True,
    )
    prices = prices.mutate(
        Symbol=prices.filename.re_extract(r'([^/]+)\.parquet$', 1)
            .replace('PRN__table', 'PRN'),
        trading_date=prices.Date.cast('date'),
    )
    qualifying = prices.filter(
        (prices.trading_date >= ibis.date('2015-01-01'))
        & (prices.trading_date < ibis.date('2016-01-01'))
        & (prices['Adj Close'] > 200)
    )
    result = (
        qualifying.join(etfs, 'Symbol')
        .group_by(qualifying.Symbol)
        .aggregate(max_adjusted_close=qualifying['Adj Close'].max())
        .order_by('Symbol')
    )
    rows = result.to_pyarrow().to_pylist()
    output = Path('/workspace/work')
    (output / 'qualifying_etfs.json').write_text(json.dumps(rows, indent=2))
    symbols = [r['Symbol'] for r in rows]
    answer = f"{', '.join(symbols)}. Total: {len(symbols)} ETFs."
    (output / 'answer.json').write_text(json.dumps({'answer': answer}))
    print(answer)


if __name__ == '__main__':
    main()
