import json
from pathlib import Path
import ibis

con = ibis.duckdb.connect()
trade = con.read_parquet('/workspace/data/indextrade/index_trade.parquet')
# The dataset's US and Canadian indices map to New York, NASDAQ, and Toronto.
names = {'NYA': 'NYSE Composite', 'IXIC': 'NASDAQ Composite', 'GSPTSE': 'S&P/TSX Composite'}
d = trade.Date
parsed = ibis.cases(
    (d.re_search(r'^\d{4}-'), d), else_=ibis.null()
).as_timestamp('%Y-%m-%d %H:%M:%S').coalesce(
    ibis.cases((d.re_search(r'^\d{2} [A-Za-z]'), d), else_=ibis.null()).as_timestamp('%d %b %Y, %H:%M'),
    ibis.cases((d.re_search(r'^[A-Za-z]'), d), else_=ibis.null()).as_timestamp('%B %d, %Y at %I:%M %p')
)
trade = trade.mutate(trading_date=parsed)
assert trade.filter(trade.trading_date.isnull()).count().execute() == 0, 'Unparsed dates'
selected = trade.filter(trade.Index.isin(list(names)), trade.trading_date.year() == 2018)
counts = selected.group_by('Index').aggregate(
    up_days=(selected.Close > selected.Open).sum(),
    down_days=(selected.Close < selected.Open).sum(),
    total_days=selected.count()
).order_by('Index')
rows = counts.to_pyarrow().to_pylist()
Path('/workspace/work/counts.json').write_text(json.dumps(rows, indent=2))
winners = counts.filter(counts.up_days > counts.down_days).to_pyarrow().to_pylist()
answer = '; '.join(f"{names[r['Index']]} ({r['Index']}): {r['up_days']} up days, {r['down_days']} down days" for r in winners) + '.'
Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
print(json.dumps(rows))
print(answer)
