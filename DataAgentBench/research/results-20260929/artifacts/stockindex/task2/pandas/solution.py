import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
trades = pd.read_parquet(DATA / 'indextrade/index_trade.parquet')
# Geographic mapping of the North American symbols present in this dataset.
north_american = {
    'NYA': 'NYSE Composite',
    'IXIC': 'NASDAQ Composite',
    'GSPTSE': 'S&P/TSX Composite',
}
trades['Date'] = pd.to_datetime(trades['Date'], format='mixed', errors='raise')
sample = trades.loc[trades['Index'].isin(north_american) & trades['Date'].dt.year.eq(2018)].copy()
assert set(sample['Index']) == set(north_american)
sample['up_days'] = sample['Close'].gt(sample['Open'])
sample['down_days'] = sample['Close'].lt(sample['Open'])
counts = sample.groupby('Index')[['up_days', 'down_days']].sum().sort_index()
counts.to_csv(OUT / 'day_counts_2018.csv')
winners = counts.loc[counts.up_days.gt(counts.down_days)]
answer = '; '.join(
    f'{north_american[symbol]} ({symbol}): {int(row.up_days)} up days, {int(row.down_days)} down days'
    for symbol, row in winners.iterrows()
) + '.'
with (OUT / 'answer.json').open('w') as f:
    json.dump({'answer': answer}, f)
print(counts.to_string())
print(answer)
