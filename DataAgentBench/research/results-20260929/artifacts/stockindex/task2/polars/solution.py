import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
# Geographic classification of the observed index symbols:
# NYA and IXIC track United States markets; GSPTSE tracks Canada.
north_american = {'NYA': 'NYSE Composite', 'IXIC': 'NASDAQ Composite', 'GSPTSE': 'S&P/TSX Composite'}
trades = pl.read_parquet(DATA / 'indextrade/index_trade.parquet')
formats = ['%Y-%m-%d %H:%M:%S', '%d %b %Y, %H:%M', '%B %d, %Y at %I:%M %p']
trades = trades.with_columns(pl.coalesce([
    pl.col('Date').str.strptime(pl.Datetime, format=fmt, strict=False)
    for fmt in formats
]).alias('parsed_date'))
assert trades['parsed_date'].null_count() == 0, 'Unparsed dates'
counts = (trades.filter(pl.col('Index').is_in(list(north_american)) & (pl.col('parsed_date').dt.year() == 2018))
    .group_by('Index').agg(
        (pl.col('Close') > pl.col('Open')).sum().alias('up_days'),
        (pl.col('Close') < pl.col('Open')).sum().alias('down_days'),
        (pl.col('Close') == pl.col('Open')).sum().alias('unchanged_days'),
        pl.len().alias('trading_days'))
    .sort('Index'))
counts.write_csv(OUT / '2018_day_counts.csv')
winners = counts.filter(pl.col('up_days') > pl.col('down_days'))
answer = '; '.join(f"{north_american[r['Index']]} ({r['Index']}): {r['up_days']} up days and {r['down_days']} down days" for r in winners.iter_rows(named=True)) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(counts)
print(answer)

if __name__ == '__main__':
    pass
