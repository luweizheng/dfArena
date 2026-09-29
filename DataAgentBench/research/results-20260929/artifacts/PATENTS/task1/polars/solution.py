import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    definitions = pl.read_parquet(DATA / 'CPCDefinition/cpc_definition.parquet', columns=['symbol', 'level'])
    groups = definitions.filter(pl.col('level') == 5).select(pl.col('symbol').alias('group')).unique()
    assert groups.filter(~pl.col('group').str.contains(r'^[A-HY]\d{2}[A-Z]$')).is_empty()
    publications = pl.read_parquet(DATA / 'publication/publicationinfo.parquet', columns=['filing_date', 'cpc']).with_row_index('patent')
    # Structured text uses literal backslash-n separators; normalize before decoding.
    entries_type = pl.List(pl.Struct({'code': pl.String, 'first': pl.Boolean}))
    primary = (
        publications.with_columns(
            pl.col('filing_date').str.extract(r'\b(\d{4})\b', 1).cast(pl.Int32).alias('year'),
            pl.col('cpc').str.replace_all(r'\\n', '\n').str.json_decode(entries_type).alias('entries'),
        )
        .select('patent', 'year', 'entries').drop_nulls(['year', 'entries'])
        .explode('entries').unnest('entries').filter(pl.col('first') == True)
        .with_columns(pl.col('code').str.extract(r'^([A-HY]\d{2}[A-Z])', 1).alias('group'))
        .join(groups, on='group', how='inner')
        .select('patent', 'year', 'group').unique()
    )
    counts = primary.group_by('group', 'year').len(name='filings')
    years = counts.group_by('group').agg(pl.int_ranges(pl.col('year').min(), pl.col('year').max() + 1).alias('year')).explode('year').with_columns(pl.col('year').cast(pl.Int32))
    annual = (
        years.join(counts, on=['group', 'year'], how='left')
        .with_columns(pl.col('filings').fill_null(0))
        .sort(['group', 'year'])
        .with_columns(pl.col('filings').ewm_mean(alpha=0.2, adjust=False).over('group').alias('ema'))
    )
    # Sorting ascending by year ensures the earliest year wins an exact tie.
    best = annual.sort(['group', 'ema', 'year'], descending=[False, True, False]).unique('group', keep='first', maintain_order=True)
    result = best.filter(pl.col('year') == 2022).sort('group')
    annual.write_csv(OUT / 'annual_ema.csv')
    best.sort('group').write_csv(OUT / 'best_years.csv')
    answer = ', '.join(result['group'].to_list())
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(json.dumps({'answer': answer}))
    print(f'Counted {primary.height} patent/group pairs across {counts["group"].n_unique()} groups; {result.height} peak in 2022.')

if __name__ == '__main__':
    main()
