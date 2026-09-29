import json
from pathlib import Path
import re
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
info = pd.read_parquet(DATA / 'stockinfo/stockinfo.parquet')
eligible = info.loc[info['Listing Exchange'].eq('N') & info['ETF'].eq('N')]
records = []
for _, stock in eligible.iterrows():
    symbol = stock['Symbol']
    filename = 'PRN__table' if symbol == 'PRN' else symbol
    prices = pd.read_parquet(DATA / 'stocktrade' / f'{filename}.parquet', columns=['Date', 'Open', 'Close'])
    dates = pd.to_datetime(prices['Date'], errors='raise')
    year = prices.loc[dates.dt.year.eq(2017)]
    up = int(year['Close'].gt(year['Open']).sum())
    down = int(year['Close'].lt(year['Open']).sum())
    records.append({'symbol': symbol, 'description': stock['Company Description'], 'up': up, 'down': down, 'difference': up-down})
ranked = pd.DataFrame(records).query('difference > 0').sort_values(['difference', 'symbol'], ascending=[False, True])
ranked.to_csv(OUT / 'ranked_stocks.csv', index=False)
print(ranked.head(10).to_string(index=False))
# Names are the leading noun phrases in the source company descriptions.
def company_name(description):
    return re.split(r'\s+(?:is\b|specializes\b|provides\b|offers\b|focuses\b|invests\b)', description, maxsplit=1)[0].strip()

top = ranked.head(5)
assert len(top) == 5
assert ranked.iloc[4]['difference'] > ranked.iloc[5]['difference']
names = top['description'].map(company_name).tolist()
answer = {'answer': '; '.join(names)}
(OUT / 'answer.json').write_text(json.dumps(answer, ensure_ascii=False) + '\n')
print(json.dumps(answer, ensure_ascii=False))
