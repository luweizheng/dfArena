import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    info = con.read_parquet('/workspace/data/stockinfo/stockinfo.parquet')
    matches = info.filter(
        info['Company Description'].startswith('The RealReal, Inc.')
    ).select('Symbol').distinct().to_pyarrow().to_pylist()
    if len(matches) != 1:
        raise ValueError(f'Expected one company, found {matches}')
    symbol = matches[0]['Symbol']
    prices = con.read_parquet(f'/workspace/data/stocktrade/{symbol}.parquet')
    yearly = prices.filter(prices['Date'].cast('date').year() == 2020)
    maximum = yearly['Adj Close'].max().execute()
    if maximum is None:
        raise ValueError('No adjusted closing prices found for 2020')
    answer = {'answer': f'The maximum adjusted closing price for The RealReal, Inc. in 2020 was ${maximum:.2f}.'}
    Path('/workspace/work/answer.json').write_text(json.dumps(answer) + '\n')
    print(f'Maximum (unrounded): {maximum}')
    print(json.dumps(answer))


if __name__ == '__main__':
    main()
