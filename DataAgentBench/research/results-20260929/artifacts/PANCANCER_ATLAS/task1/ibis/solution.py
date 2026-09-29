import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    clinical = con.read_parquet('/workspace/data/clinical/clinical_info.parquet')
    expression = con.read_parquet('/workspace/data/molecular/RNASeq_Expression.parquet')
    histology = clinical.icd_o_3_histology.strip()
    patients = clinical.filter(
        clinical.Patient_description.lower().contains('brain lower grade glioma'),
        histology.notnull(),
        histology != '',
        ~histology.re_search(r'^\[.*\]$'),
    ).select(
        barcode=clinical.Patient_description.re_extract(r'(TCGA-[A-Za-z0-9]{2}-[A-Za-z0-9]{4})', 1),
        histology=histology,
    )
    count = expression.normalized_count
    igf2 = expression.filter(
        expression.Symbol == 'IGF2',
        count.notnull(),
        ~count.isnan(),
        ~count.isinf(),
        count >= 0,
    ).select('ParticipantBarcode', 'normalized_count')
    joined = patients.inner_join(igf2, patients.barcode == igf2.ParticipantBarcode)
    result = joined.group_by('histology').aggregate(
        mean_log10_expression=(joined.normalized_count + 1).log10().mean(),
        samples=joined.count(),
        patients=joined.barcode.nunique(),
    ).order_by('histology')
    rows = result.to_pyarrow().to_pylist()
    assert rows, 'No eligible LGG expression records found'
    answer = 'Mean log10(IGF2 normalized_count + 1) by ICD-O-3 histology: ' + '; '.join(
        f"{row['histology']}: {row['mean_log10_expression']:.6f}" for row in rows
    ) + '.'
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(json.dumps(rows, indent=2))
    print(answer)


if __name__ == '__main__':
    main()
