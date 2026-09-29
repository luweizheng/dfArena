import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

def main():
    clinical = (
        pl.scan_parquet(DATA / 'clinical/clinical_info.parquet')
        .filter(pl.col('Patient_description').str.contains('(?i)Brain lower grade glioma'))
        .select(
            pl.col('Patient_description').str.extract(r'(TCGA-[A-Za-z0-9]{2}-[A-Za-z0-9]{4})', 1).alias('ParticipantBarcode'),
            pl.col('icd_o_3_histology').str.strip_chars(),
        )
        .filter(
            pl.col('icd_o_3_histology').is_not_null()
            & (pl.col('icd_o_3_histology') != '')
            & ~pl.col('icd_o_3_histology').str.contains(r'^\[.*\]$')
        )
        .collect()
    )
    assert clinical['ParticipantBarcode'].null_count() == 0
    assert clinical['ParticipantBarcode'].n_unique() == clinical.height
    expression = (
        pl.scan_parquet(DATA / 'molecular/RNASeq_Expression.parquet')
        .filter(
            (pl.col('Symbol') == 'IGF2')
            & pl.col('normalized_count').is_not_null()
            & pl.col('normalized_count').is_finite()
            & (pl.col('normalized_count') >= 0)
        )
        .select('ParticipantBarcode', 'normalized_count')
    )
    joined = expression.join(clinical.lazy(), on='ParticipantBarcode', how='inner').with_columns(
        (pl.col('normalized_count') + 1).log10().alias('log10_expression')
    )
    results = joined.group_by('icd_o_3_histology').agg(
        pl.col('log10_expression').mean().alias('average_log10_expression'),
        pl.len().alias('sample_count'),
        pl.col('ParticipantBarcode').n_unique().alias('patient_count'),
    ).sort('icd_o_3_histology').collect()
    results.write_csv(OUT / 'histology_averages.csv')
    answer = 'Mean log10(IGF2 normalized_count + 1) by ICD-O-3 histology for LGG: ' + '; '.join(
        f"{row['icd_o_3_histology']}: {row['average_log10_expression']:.6f}"
        for row in results.iter_rows(named=True)
    ) + '.'
    (OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(results)
    print(answer)

if __name__ == '__main__':
    main()
