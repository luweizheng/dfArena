import datetime as dt
import json
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
ASIA = {
    '000001.SS': 'Shanghai Composite',
    '399001.SZ': 'Shenzhen Component',
    'HSI': 'Hang Seng',
    'N225': 'Nikkei 225',
    'NSEI': 'Nifty 50',
    'TWII': 'Taiwan Weighted',
}

def main():
    trades = pl.read_parquet('/workspace/data/indextrade/index_trade.parquet')
    formats = ['%Y-%m-%d %H:%M:%S', '%d %b %Y, %H:%M', '%B %d, %Y at %I:%M %p']
    trades = trades.with_columns(pl.coalesce([
        pl.col('Date').str.strptime(pl.Datetime, fmt, strict=False)
        for fmt in formats
    ]).dt.date().alias('parsed_date'))
    assert trades['parsed_date'].null_count() == 0, 'Unparsed dates'
    selected = trades.filter(pl.col('Index').is_in(list(ASIA)) & (pl.col('parsed_date') >= dt.date(2020, 1, 1)))
    valid = pl.all_horizontal([pl.col(c).is_not_null() & pl.col(c).is_finite() for c in ['Open', 'High', 'Low']]) & (pl.col('Open') > 0)
    assert selected.filter(~valid).height == 0, 'Invalid prices'
    results = (selected.with_columns(((pl.col('High') - pl.col('Low')) / pl.col('Open')).alias('intraday_volatility'))
        .group_by('Index').agg(pl.col('intraday_volatility').mean().alias('average_intraday_volatility'), pl.len().alias('days'), pl.col('parsed_date').min().alias('start'), pl.col('parsed_date').max().alias('end'))
        .sort('average_intraday_volatility', descending=True))
    results.write_csv(OUT / 'volatility_by_index.csv')
    winner = results.row(0, named=True)
    answer = f"The {ASIA[winner['Index']]} index ({winner['Index']}) had the highest average intraday volatility since 2020, at {winner['average_intraday_volatility']:.2%} (mean of (High - Low) / Open)."
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(results)
    print(answer)

if __name__ == '__main__':
    main()
