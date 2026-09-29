from pathlib import Path
import json
import re
import ibis

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
info = con.read_parquet(str(DATA / 'stockinfo/stockinfo.parquet'))
troubled = info.filter(
    (info['Listing Exchange'] == 'Q')
    & info['Financial Status'].isin(['D', 'E', 'G', 'H', 'J', 'K'])
)
# Materialize only the symbols needed to locate the separate price tables.
symbols = troubled.select('Symbol').distinct().to_pyarrow().column('Symbol').to_pylist()
parts = []
for symbol in symbols:
    filename = 'PRN__table' if symbol == 'PRN' else symbol
    t = con.read_parquet(str(DATA / 'stocktrade' / (filename + '.parquet')))
    t = t.mutate(trading_date=t['Date'].cast('date'))
    t = t.filter((t.trading_date.year() == 2008) & t.Volume.notnull())
    parts.append(t.select(Symbol=ibis.literal(symbol), Volume=t.Volume.cast('float64')))
volumes = ibis.union(*parts)
averages = volumes.group_by('Symbol').aggregate(
    average_daily_volume=volumes.Volume.mean(), nonnull_days=volumes.Volume.count()
)
result = troubled.join(averages, 'Symbol').select(
    troubled.Symbol, troubled['Company Description'],
    averages.average_daily_volume, averages.nonnull_days
).order_by('Symbol')
rows = result.to_pyarrow().to_pylist()
(OUT / 'results.json').write_text(json.dumps(rows, indent=2))
# Names are the introductory portion of the supplied company descriptions.
def company_name(description):
    return re.split(r' specializes in | provides | is at | is an | is dedicated to | harnesses | offers |, based in ', description, maxsplit=1)[0].strip()
items = [f"{company_name(r['Company Description'])} ({r['Symbol']}): {r['average_daily_volume']:,.2f}" for r in rows]
answer = 'Average daily trading volume in 2008 (shares/day, excluding null volumes): ' + '; '.join(items) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(answer)
