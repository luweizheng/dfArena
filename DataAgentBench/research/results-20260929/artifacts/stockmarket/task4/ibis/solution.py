import json
import re
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
info = con.read_parquet('/workspace/data/stockinfo/stockinfo.parquet')
eligible = info.filter((info['Listing Exchange'] == 'N') & (info.ETF == 'N')).select('Symbol', 'Company Description')
prices = con.read_parquet('/workspace/data/stocktrade/*.parquet', filename=True)
symbol = prices.filename.re_extract(r'([^/]+)\.parquet$', 1)
prices = prices.mutate(Symbol=ibis.ifelse(symbol == 'PRN__table', 'PRN', symbol), trading_date=prices.Date.cast('date'))
prices = prices.filter((prices.trading_date >= ibis.date('2017-01-01')) & (prices.trading_date < ibis.date('2018-01-01')))
prices = prices.semi_join(eligible, 'Symbol')
counts = prices.group_by('Symbol').aggregate(up_days=(prices.Close > prices.Open).sum(), down_days=(prices.Close < prices.Open).sum())
counts = counts.mutate(difference=counts.up_days-counts.down_days)
ranked = counts.filter(counts['difference'] > 0).join(eligible, 'Symbol').order_by(ibis.desc('difference'), 'Symbol')
rows = ranked.limit(10).to_pyarrow().to_pylist()
(OUT / 'ranking.json').write_text(json.dumps(rows, indent=2))
def company_name(description):
    return re.split(r'\s+(?:is|specializes|provides|offers|focuses|invests|operates)\b', description, maxsplit=1)[0].strip()

answer = '; '.join(company_name(row['Company Description']) for row in rows[:5])
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps(rows, indent=2))

if len(rows) < 5:
    raise RuntimeError('Fewer than five eligible stocks')
