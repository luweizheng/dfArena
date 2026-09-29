from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    info = pl.read_parquet(DATA / 'stockinfo/stockinfo.parquet')
    candidates = info.filter(
        (pl.col('Listing Exchange') == 'P') & (pl.col('ETF') == 'Y')
    ).select('Symbol', 'Company Description').unique(subset=['Symbol']).sort('Symbol')
    results = []
    for symbol in candidates['Symbol']:
        filename = 'PRN__table' if symbol == 'PRN' else symbol
        prices = pl.scan_parquet(DATA / 'stocktrade' / f'{filename}.parquet')
        peak = prices.filter(
            (pl.col('Date') >= '2015-01-01') & (pl.col('Date') < '2016-01-01')
        ).select(pl.col('Adj Close').max().alias('Max Adjusted Close 2015')).collect()
        results.append({'Symbol': symbol, 'Max Adjusted Close 2015': peak.item()})
    peaks = pl.DataFrame(results, schema={'Symbol': pl.String, 'Max Adjusted Close 2015': pl.Float64})
    qualifying = candidates.join(peaks, on='Symbol').filter(
        pl.col('Max Adjusted Close 2015').is_not_null()
        & pl.col('Max Adjusted Close 2015').is_finite()
        & (pl.col('Max Adjusted Close 2015') > 200)
    ).sort('Symbol')
    qualifying.write_csv(OUT / 'qualifying_etfs.csv')
    symbols = qualifying['Symbol'].to_list()
    answer = f"{len(symbols)} ETFs: {', '.join(symbols)}."
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(answer)

if __name__ == '__main__':
    main()
