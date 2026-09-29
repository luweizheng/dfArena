import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
info = pd.read_parquet(DATA / 'stockinfo/stockinfo.parquet')
companies = info.loc[info['Market Category'].eq('S')]
results = []
for _, company in companies.iterrows():
    symbol = company['Symbol']
    filename = 'PRN__table' if symbol == 'PRN' else symbol
    prices = pd.read_parquet(DATA / 'stocktrade' / f'{filename}.parquet', columns=['Date', 'High', 'Low'])
    dates = pd.to_datetime(prices['Date'])
    qualifying = dates.dt.year.eq(2019) & ((prices['High'] - prices['Low']) > 0.20 * prices['Low'])
    count = dates.loc[qualifying].dt.normalize().nunique()
    results.append({'Symbol': symbol, 'days': int(count), 'description': company['Company Description']})
ranked = pd.DataFrame(results).sort_values(['days', 'Symbol'], ascending=[False, True])
ranked.to_csv(OUT / 'ranked_companies.csv', index=False)
top = ranked.head(5)
# Company descriptions begin with the company name followed by a descriptive verb.
names = [re.split(r'\s+(?:is|specializes|provides|focuses|operates|offers|engages|develops|designs)\b', description, maxsplit=1)[0] for description in top['description']]
(OUT / 'answer.json').write_text(json.dumps({'answer': '; '.join(names)}, ensure_ascii=False) + '\n')
print(ranked.head(10).to_string(index=False))
print((OUT / 'answer.json').read_text())
