import datetime
import json
from pathlib import Path
import ibis

@ibis.udf.scalar.builtin
def try_strptime(value: str, formats: list[str]) -> datetime.datetime:
    ...


def main():
    con = ibis.duckdb.connect()
    trades = con.read_parquet('/workspace/data/indextrade/index_trade.parquet')
    # The dataset has no region or join key; map the Asian index symbols
    # to their established index names using the exchange geography.
    asia = {
        'HSI': 'Hang Seng Index',
        '000001.SS': 'Shanghai Composite Index',
        '399001.SZ': 'Shenzhen Component Index',
        'N225': 'Nikkei 225',
        'NSEI': 'Nifty 50',
        'TWII': 'Taiwan Capitalization Weighted Stock Index',
    }
    dated = trades.mutate(trade_date=try_strptime(trades.Date, [
        '%Y-%m-%d %H:%M:%S', '%d %b %Y, %H:%M',
        '%B %d, %Y at %I:%M %p',
    ]).date())
    invalid_dates = dated.filter(dated.trade_date.isnull()).count().execute()
    if invalid_dates:
        raise ValueError(f'{invalid_dates} dates could not be parsed')
    selected = dated.filter(
        dated.Index.isin(list(asia)),
        dated.trade_date >= ibis.date('2020-01-01'),
        dated.Open.notnull(), dated.Open != 0,
        dated.High.notnull(), dated.Low.notnull(),
    )
    selected = selected.mutate(volatility=(selected.High-selected.Low)/selected.Open)
    ranking = selected.group_by('Index').aggregate(
        average_intraday_volatility=selected.volatility.mean(),
        trading_days=selected.count(),
        first_date=selected.trade_date.min(),
        last_date=selected.trade_date.max(),
    ).order_by(ibis.desc('average_intraday_volatility'))
    rows = ranking.to_pyarrow().to_pylist()
    Path('/workspace/work/ranking.json').write_text(json.dumps(rows, default=str, indent=2))
    winner = rows[0]
    answer = (f"{asia[winner['Index']]} ({winner['Index']}) had the highest average "
              f"intraday volatility since 2020, at {winner['average_intraday_volatility']:.4%} "
              f"(mean of (High - Low) / Open).")
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
    print(answer)
    print(json.dumps(rows, default=str, indent=2))

if __name__ == '__main__':
    main()
