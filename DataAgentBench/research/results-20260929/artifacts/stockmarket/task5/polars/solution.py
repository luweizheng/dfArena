from pathlib import Path
import json
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    companies = pl.read_parquet(DATA / 'stockinfo/stockinfo.parquet').filter(
        pl.col('Market Category') == 'S'
    )
    counts = []
    for symbol in companies['Symbol'].unique().sort():
        filename = 'PRN__table' if symbol == 'PRN' else symbol
        qualifying = (
            pl.scan_parquet(DATA / 'stocktrade' / f'{filename}.parquet')
            .filter(
                (pl.col('Date') >= '2019-01-01')
                & (pl.col('Date') < '2020-01-01')
                & ((pl.col('High') - pl.col('Low')) > 0.2 * pl.col('Low'))
            )
            .select(pl.col('Date').n_unique().alias('days'))
            .collect()
        )
        counts.append({'Symbol': symbol, 'days': qualifying['days'][0]})
    ranked = companies.join(pl.DataFrame(counts), on='Symbol').sort(
        ['days', 'Symbol'], descending=[True, False]
    )
    ranked.write_json(OUT / 'rankings.json')
    top = ranked.head(5)
    # Descriptions begin with the company name, followed by its business summary.
    names = top['Company Description'].str.extract(r'^(.*?)(?: specializes in | is involved in | engages in | is dedicated to )', 1).to_list()
    (OUT / 'answer.json').write_text(json.dumps({'answer': '; '.join(names)}, ensure_ascii=False) + '\n')
    for row in ranked.head(8).select('Symbol', 'days', 'Company Description').iter_rows(named=True):
        print(json.dumps(row))

if __name__ == '__main__':
    main()
