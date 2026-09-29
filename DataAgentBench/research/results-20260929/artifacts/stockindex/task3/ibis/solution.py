import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
@ibis.udf.scalar.builtin
def try_strptime(arg: str, format: list[str]) -> ibis.expr.datatypes.timestamp:
    ...

t = con.read_parquet('/workspace/data/indextrade/index_trade.parquet')
formats = ['%Y-%m-%d %H:%M:%S', '%d %b %Y, %H:%M', '%B %d, %Y at %I:%M %p', '%Y-%m-%d']
t = t.mutate(trade_date=try_strptime(t.Date, formats).cast('date'))
assert t.filter(t.trade_date.isnull()).count().execute() == 0, 'Unparsed dates'
t = t.filter(t.trade_date >= ibis.date('2000-01-01'), t.CloseUSD.notnull(), t.CloseUSD > 0)
coverage = t.group_by('Index').aggregate(start=t.trade_date.min(), end=t.trade_date.max(), rows=t.count()).order_by('Index')
print(coverage.to_pyarrow().to_pylist())
t = t.mutate(month=t.trade_date.truncate('M'))
monthly = t.group_by('Index', 'month').aggregate(purchase_price=t.CloseUSD.argmin(t.trade_date))
portfolio = monthly.group_by('Index').aggregate(units=(1.0/monthly.purchase_price).sum(), contributions=monthly.count())
latest = t.group_by('Index').aggregate(final_price=t.CloseUSD.argmax(t.trade_date), final_date=t.trade_date.max())
r = portfolio.join(latest, 'Index').mutate(return_pct=(ibis._.units * ibis._.final_price / ibis._.contributions - 1)*100).order_by(ibis.desc('return_pct'))
rows = r.to_pyarrow().to_pylist()
print(rows)
(OUT/'calculations.json').write_text(json.dumps(rows, default=str, indent=2))
names = {
'IXIC': ('NASDAQ Composite', 'United States'),
'NYA': ('NYSE Composite', 'United States'),
'HSI': ('Hang Seng', 'Hong Kong, China'),
'000001.SS': ('Shanghai Composite', 'China'),
'399001.SZ': ('Shenzhen Component', 'China'),
'N225': ('Nikkei 225', 'Japan'),
'N100': ('Euronext 100', 'multiple European countries'),
'GSPTSE': ('S&P/TSX Composite', 'Canada'),
'NSEI': ('NIFTY 50', 'India'),
'GDAXI': ('DAX', 'Germany'),
'SSMI': ('Swiss Market Index', 'Switzerland'),
'TWII': ('Taiwan Weighted Index', 'Taiwan'),
'J203.JO': ('FTSE/JSE All Share', 'South Africa'),
}
parts = [f"{i}. {names[x['Index']][0]} ({x['Index']}) — {names[x['Index']][1]}: {x['return_pct']:.1f}%" for i,x in enumerate(rows[:5],1)]
answer = 'Equal monthly investments from January 2000 (or earliest available data), buying at each month’s first available USD closing price and valuing at each index’s final observation: ' + '; '.join(parts) + '. Returns are gains relative to total contributions.'
(OUT/'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False))
