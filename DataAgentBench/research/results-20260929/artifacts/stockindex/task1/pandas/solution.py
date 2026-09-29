import json
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
prices = pd.read_parquet(DATA / 'indextrade/index_trade.parquet')
# Geographic mapping of the Asian index symbols present in the price table.
asian_indices = {
    '000001.SS': 'Shanghai Composite',
    '399001.SZ': 'Shenzhen Component',
    'HSI': 'Hang Seng Index',
    'N225': 'Nikkei 225',
    'NSEI': 'Nifty 50',
    'TWII': 'Taiwan Weighted Index',
}
prices['Date'] = pd.to_datetime(prices['Date'], format='mixed', errors='raise')
selected = prices.loc[prices['Index'].isin(asian_indices) & prices['Date'].ge('2020-01-01')].copy()
selected['volatility'] = ((selected['High'] - selected['Low']) / selected['Open']).replace([np.inf, -np.inf], np.nan)
summary = selected.groupby('Index').agg(average_volatility=('volatility', 'mean'), observations=('volatility', 'count'), first_date=('Date', 'min'), last_date=('Date', 'max')).sort_values('average_volatility', ascending=False)
summary.to_csv(OUT / 'volatility_summary.csv')
winner = summary.index[0]
value = summary.loc[winner, 'average_volatility']
answer = f"{asian_indices[winner]} ({winner}) had the highest average intraday volatility since 2020, at {value:.4%}."
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(summary.to_string())
print(answer)
