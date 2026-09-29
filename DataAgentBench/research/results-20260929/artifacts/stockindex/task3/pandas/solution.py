import json
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
prices = pd.read_parquet(ROOT / 'indextrade/index_trade.parquet')
prices['Date'] = pd.to_datetime(prices['Date'], format='mixed', errors='raise')
prices = prices.loc[prices['Date'].ge('2000-01-01')].copy()
prices = prices.loc[prices['CloseUSD'].notna() & prices['CloseUSD'].gt(0)]
prices = prices.sort_values(['Index', 'Date'])
prices['month'] = prices['Date'].dt.to_period('M')
# One equal dollar contribution per month, purchasing at its first valid close.
# Fractional units are allowed; no fees, taxes, or separately paid dividends.
purchases = prices.drop_duplicates(['Index', 'month'], keep='first').copy()
purchases['units'] = 1.0 / purchases['CloseUSD']
summary = purchases.groupby('Index').agg(
    contributions=('units', 'size'), units=('units', 'sum'), start=('Date', 'min'))
terminal = prices.drop_duplicates('Index', keep='last').set_index('Index')
summary['end'] = terminal['Date']
summary['terminal_price'] = terminal['CloseUSD']
summary['ending_value'] = summary['units'] * summary['terminal_price']
summary['return_pct'] = (summary['ending_value'] / summary['contributions'] - 1) * 100
summary = summary.sort_values('return_pct', ascending=False)
# Geographic identity is domain metadata, not a join on the exchange name.
identities = {
    'IXIC': ('NASDAQ Composite', 'United States'),
    'NSEI': ('Nifty 50', 'India'),
    '399001.SZ': ('Shenzhen Component', 'China'),
    'GDAXI': ('DAX', 'Germany'),
    'TWII': ('Taiwan Weighted', 'Taiwan'),
    '000001.SS': ('Shanghai Composite', 'China'),
    'GSPTSE': ('S&P/TSX Composite', 'Canada'),
    'HSI': ('Hang Seng', 'Hong Kong, China'),
    'J203.JO': ('FTSE/JSE All Share', 'South Africa'),
    'N100': ('Euronext 100', 'multiple European countries'),
    'N225': ('Nikkei 225', 'Japan'),
    'NYA': ('NYSE Composite', 'United States'),
    'SSMI': ('Swiss Market Index', 'Switzerland'),
}
summary.to_csv(OUT / 'monthly_investment_returns.csv')
top = summary.head(5)
entries = [f'{i}. {identities[symbol][0]} ({symbol}) — {identities[symbol][1]}: {row.return_pct:.2f}%'
           for i, (symbol, row) in enumerate(top.iterrows(), 1)]
answer = ('Equal monthly investments at each month’s first available USD close, valued at each index’s latest recorded close (May–June 2021), yield: '
          + '; '.join(entries) + '. Returns are gains divided by total contributions. '
          'Nifty 50 history begins in September 2007, so its return covers that shorter period; the other top-five histories begin in January 2000.')
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False) + '\n')
print(answer)
