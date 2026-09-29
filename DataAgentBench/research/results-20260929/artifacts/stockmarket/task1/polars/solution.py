import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
metadata = pl.read_parquet(DATA / 'stockinfo/stockinfo.parquet')
company = metadata.filter(pl.col('Company Description').str.starts_with('The RealReal, Inc.'))
symbols = company.get_column('Symbol').unique().to_list()
assert len(symbols) == 1, symbols
prices = pl.read_parquet(DATA / 'stocktrade' / f'{symbols[0]}.parquet')
year_prices = prices.filter(pl.col('Date').str.slice(0, 4) == '2020')
maximum = year_prices.select(pl.col('Adj Close').max()).item()
assert maximum is not None
answer = {'answer': f'The maximum adjusted closing price in 2020 for The RealReal, Inc. was ${maximum:.2f}.'}
Path('/workspace/work/answer.json').write_text(json.dumps(answer) + '\n')
print(json.dumps({'symbol': symbols[0], 'rows_in_2020': year_prices.height, 'maximum': maximum, 'answer': answer}))
