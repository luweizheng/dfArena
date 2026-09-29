from pathlib import Path
import json
import re
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
info = pd.read_parquet(DATA / 'stockinfo/stockinfo.parquet')
# Include every status containing deficiency or delinquency, including bankruptcy combinations.
candidates = info.loc[info['Listing Exchange'].eq('Q') & info['Financial Status'].isin(['D', 'E', 'G', 'H', 'J', 'K'])]
results = []
for _, company in candidates.iterrows():
    symbol = company['Symbol']
    filename = 'PRN__table' if symbol == 'PRN' else symbol
    prices = pd.read_parquet(DATA / 'stocktrade' / f'{filename}.parquet', columns=['Date', 'Volume'])
    dates = pd.to_datetime(prices['Date'], errors='raise')
    volumes = prices.loc[dates.dt.year.eq(2008), 'Volume'].dropna()
    if volumes.empty:
        continue
    description = company['Company Description']
    name = re.split(r' specializes\b| is an?\b| is at\b| is dedicated\b| provides\b| harnesses\b| offers\b|, based in\b', description, maxsplit=1)[0].strip()
    results.append({'company': name, 'symbol': symbol, 'average_daily_volume': float(volumes.mean()), 'non_null_days': int(volumes.count())})
result = pd.DataFrame(results).sort_values('company')
result.to_csv(OUT / 'volume_calculations.csv', index=False)
lines = [f"{r.company} ({r.symbol}): {r.average_daily_volume:,.6f}" for r in result.itertuples()]
answer = 'Average daily trading volume in 2008 (shares/day; non-null observations): ' + '; '.join(lines) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(answer)
print(f'Companies: {len(result)}')
