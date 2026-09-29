import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
metadata = pd.read_parquet(DATA / 'stockinfo/stockinfo.parquet')
companies = metadata.loc[metadata['Company Description'].str.startswith('The RealReal, Inc.', na=False)]
assert len(companies) == 1, 'Expected a unique company match'
symbol = companies.iloc[0]['Symbol']
prices = pd.read_parquet(DATA / 'stocktrade' / f'{symbol}.parquet')
dates = pd.to_datetime(prices['Date'], errors='raise')
year_prices = prices.loc[dates.dt.year.eq(2020)]
maximum = year_prices['Adj Close'].max()
assert pd.notna(maximum), 'No adjusted closing prices found for 2020'
answer = {'answer': f'${maximum:.2f}'}
Path('/workspace/work/answer.json').write_text(json.dumps(answer) + '\n')
print(f'Ticker: {symbol}; 2020 rows: {len(year_prices)}; maximum: {maximum!r}')
print(json.dumps(answer))
