from pathlib import Path
import json
import ibis


def main():
    con = ibis.duckdb.connect()
    clinical = con.read_parquet('/workspace/data/clinical/clinical_info.parquet')
    mutations = con.read_parquet('/workspace/data/molecular/Mutation_Data.parquet')
    description = clinical.Patient_description.lower()
    patients = clinical.filter(
        description.contains('breast invasive carcinoma'),
        description.re_search(r'\balive\b'),
        clinical.histological_type.notnull(),
    ).select(
        barcode=clinical.Patient_description.re_extract(r'(TCGA-[A-Za-z0-9]{2}-[A-Za-z0-9]{4})', 1),
        histological_type=clinical.histological_type,
    ).distinct()
    # One mutation-positive indicator per patient, regardless of mutation count.
    carriers = mutations.filter(mutations.Hugo_Symbol == 'CDH1').select(
        barcode=mutations.ParticipantBarcode,
    ).distinct().mutate(has_mutation=ibis.literal(1))
    joined = patients.left_join(carriers, 'barcode')
    counts = joined.group_by('histological_type').aggregate(
        total_patients=joined.barcode.nunique(),
        mutated_patients=joined.has_mutation.fill_null(0).sum(),
    )
    ranked = counts.mutate(
        percentage=100.0 * counts.mutated_patients / counts.total_patients
    ).order_by(ibis.desc('percentage'), 'histological_type')
    rows = ranked.to_pyarrow().to_pylist()
    Path('/workspace/work/results.json').write_text(json.dumps(rows, indent=2))
    answer = '; '.join(
        f"{row['histological_type']}: {row['percentage']:.2f}% "
        f"({row['mutated_patients']}/{row['total_patients']} patients)"
        for row in rows[:3]
    ) + '.'
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}))
    print(answer)


if __name__ == '__main__':
    main()
