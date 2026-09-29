import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    # Each denominator includes all living BRCA patients of that histological type.
    patients = (
        pl.scan_parquet(DATA / 'clinical/clinical_info.parquet')
        .filter(
            pl.col('Patient_description').str.contains('(?i)Breast invasive carcinoma|\\bBRCA\\b')
            & pl.col('Patient_description').str.contains('(?i)\\bAlive\\b')
        )
        .select(
            pl.col('Patient_description').str.extract(r'(TCGA-[A-Za-z0-9]{2}-[A-Za-z0-9]{4})', 1).alias('ParticipantBarcode'),
            'histological_type',
        )
        .unique()
        .collect()
    )
    assert patients['ParticipantBarcode'].null_count() == 0
    assert patients['ParticipantBarcode'].n_unique() == patients.height
    # Count mutation presence once per patient, regardless of mutation/sample count.
    mutations = (
        pl.scan_parquet(DATA / 'molecular/Mutation_Data.parquet')
        .filter(pl.col('Hugo_Symbol') == 'CDH1')
        .select('ParticipantBarcode')
        .unique()
        .with_columns(pl.lit(True).alias('has_CDH1_mutation'))
        .collect()
    )
    results = (
        patients.join(mutations, on='ParticipantBarcode', how='left')
        .with_columns(pl.col('has_CDH1_mutation').fill_null(False))
        .filter(pl.col('histological_type').is_not_null())
        .group_by('histological_type')
        .agg(pl.len().alias('total_patients'), pl.col('has_CDH1_mutation').sum().alias('mutated_patients'))
        .with_columns((100 * pl.col('mutated_patients') / pl.col('total_patients')).alias('percentage'))
        .sort(['percentage', 'histological_type'], descending=[True, False])
    )
    results.write_csv(OUT / 'mutation_percentages.csv')
    top = results.head(3).to_dicts()
    answer = '; '.join(f"{r['histological_type']}: {r['percentage']:.2f}% ({r['mutated_patients']}/{r['total_patients']} patients)" for r in top) + '.'
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(answer)

if __name__ == '__main__':
    main()
