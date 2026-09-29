"""Rank NASDAQ Capital Market companies by qualifying distinct dates in 2019."""
import json
import re
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    info = con.read_parquet('/workspace/data/stockinfo/stockinfo.parquet')
    companies = info.filter(info['Market Category'] == 'S').select(
        symbol=info['Symbol'], company=info['Company Description']
    ).distinct()
    prices = con.read_parquet(
        '/workspace/data/stocktrade/*.parquet', filename=True, union_by_name=True
    )
    prices = prices.mutate(
        symbol=prices.filename.re_extract(r'([^/]+)\.parquet$', 1).replace('PRN__table', 'PRN'),
        trading_date=prices.Date.cast('date'),
    )
    qualifying = prices.filter(
        prices.trading_date >= ibis.date('2019-01-01'),
        prices.trading_date < ibis.date('2020-01-01'),
        (prices.High - prices.Low) > 0.20 * prices.Low,
    )
    counts = qualifying.group_by('symbol').aggregate(days=qualifying.trading_date.nunique())
    ranked = companies.join(counts, 'symbol').select(
        companies.symbol, companies.company, counts.days
    ).order_by(ibis.desc('days'), ibis.asc('symbol'))
    rows = ranked.limit(10).to_pyarrow().to_pylist()
    Path('/workspace/work/ranking.json').write_text(json.dumps(rows, indent=2))
    names = [re.split(r'\s+(?:specializes in|is involved in|engages in|is dedicated to)\s+', row['company'], maxsplit=1)[0] for row in rows[:5]]
    answer = '; '.join(names)
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
