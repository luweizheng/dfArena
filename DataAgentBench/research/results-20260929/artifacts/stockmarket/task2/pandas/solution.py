from pathlib import Path
import json
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    info = pd.read_parquet(DATA / 'stockinfo/stockinfo.parquet')
    symbols = info.loc[info['Listing Exchange'].eq('P') & info['ETF'].eq('Y'), 'Symbol'].dropna().drop_duplicates().sort_values()
    matches = []
    for symbol in symbols:
        filename = 'PRN__table' if symbol == 'PRN' else symbol
        prices = pd.read_parquet(DATA / 'stocktrade' / f'{filename}.parquet', columns=['Date', 'Adj Close'])
        dates = pd.to_datetime(prices['Date'], errors='raise')
        yearly = prices.loc[dates.ge('2015-01-01') & dates.lt('2016-01-01')]
        qualifying = yearly.loc[yearly['Adj Close'].gt(200)]
        if not qualifying.empty:
            matches.append({'Symbol': symbol, 'max_adjusted_close_2015': float(yearly['Adj Close'].max()), 'days_above_200': len(qualifying)})
    result = pd.DataFrame(matches)
    result.to_csv(OUT / 'qualifying_etfs.csv', index=False)
    answer = f"{len(matches)} ETFs: {', '.join(result['Symbol'])}."
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(answer)
    print(result.to_string(index=False))

if __name__ == '__main__':
    main()
