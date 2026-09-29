import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    clinical = pl.scan_parquet(DATA / 'clinical/clinical_info.parquet')
    patients = (
        clinical.filter(
            pl.col('Patient_description').str.contains(r'(?i)\bBreast invasive carcinoma\b')
            & pl.col('Patient_description').str.contains(r'\bFEMALE\b')
            & pl.col('histological_type').is_not_null()
            & ~pl.col('histological_type').str.strip_chars().str.to_lowercase().is_in(
                ['', 'unknown', 'not reported', 'not available', '[not available]', '[not evaluated]', '[unknown]']
            )
        )
        .select(
            pl.col('Patient_description').str.extract(r'(TCGA-[A-Za-z0-9]{2}-[A-Za-z0-9]{4})', 1).alias('ParticipantBarcode'),
            'histological_type',
        ).unique().collect()
    )
    assert patients['ParticipantBarcode'].null_count() == 0
    assert patients['ParticipantBarcode'].n_unique() == patients.height
    mutations = (
        pl.scan_parquet(DATA / 'molecular/Mutation_Data.parquet')
        .filter((pl.col('Hugo_Symbol') == 'CDH1') & (pl.col('FILTER') == 'PASS'))
        .select('ParticipantBarcode').unique()
        .with_columns(pl.lit(True).alias('mutated')).collect()
    )
    # A patient has mutation presence if at least one reliable CDH1 call exists.
    cohort = patients.join(mutations, on='ParticipantBarcode', how='left').with_columns(
        pl.col('mutated').fill_null(False)
    )
    counts = cohort.group_by('histological_type').agg(
        pl.col('mutated').sum().alias('present'),
        (~pl.col('mutated')).sum().alias('absent'),
        pl.len().alias('row_total'),
    ).sort('histological_type')
    retained = counts.filter(pl.col('row_total') > 10)
    statuses = [s for s in ['present', 'absent'] if retained[s].sum() > 10]
    assert len(statuses) == 2
    cells = retained.unpivot(on=statuses, index='histological_type', variable_name='mutation_status', value_name='observed')
    cells = cells.with_columns(
        pl.col('observed').sum().over('histological_type').alias('row_total'),
        pl.col('observed').sum().over('mutation_status').alias('column_total'),
        pl.col('observed').sum().alias('grand_total'),
    ).with_columns(
        (pl.col('row_total').cast(pl.Float64) * pl.col('column_total') / pl.col('grand_total')).alias('expected')
    ).with_columns(
        ((pl.col('observed') - pl.col('expected')).pow(2) / pl.col('expected')).alias('chi_square_contribution')
    )
    statistic = cells['chi_square_contribution'].sum()
    counts.write_csv(OUT / 'histology_counts.csv')
    cells.write_csv(OUT / 'chi_square_cells.csv')
    answer = {'answer': f'Pearson chi-square statistic: {statistic:.6f} (df = {retained.height - 1}; N = {retained["row_total"].sum()}).'}
    (OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
    print(counts)
    print(json.dumps(answer))

if __name__ == '__main__':
    main()
