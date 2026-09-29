import json
from pathlib import Path
import pandas as pd

OUT = Path('/workspace/work')
clinical = pd.read_parquet('/workspace/data/clinical/clinical_info.parquet')
desc = clinical['Patient_description']
cohort = clinical.loc[
    desc.str.contains(r'Breast invasive carcinoma|\bBRCA\b', case=False, na=False)
    & desc.str.contains(r'\bAlive\b', case=False, na=False),
    ['Patient_description', 'histological_type']
].copy()
cohort['ParticipantBarcode'] = cohort['Patient_description'].str.extract(r'(TCGA-[A-Za-z0-9]{2}-[A-Za-z0-9]{4})', expand=False)
assert cohort['ParticipantBarcode'].notna().all()
assert not cohort['ParticipantBarcode'].duplicated().any()
mutations = pd.read_parquet('/workspace/data/molecular/Mutation_Data.parquet', columns=['ParticipantBarcode', 'Hugo_Symbol'])
mutated = mutations.loc[mutations['Hugo_Symbol'].eq('CDH1'), 'ParticipantBarcode'].drop_duplicates()
cohort['CDH1_mutated'] = cohort['ParticipantBarcode'].isin(mutated)
summary = cohort.groupby('histological_type', dropna=True).agg(patients=('ParticipantBarcode', 'nunique'), mutated_patients=('CDH1_mutated', 'sum'))
summary['percentage'] = 100 * summary['mutated_patients'] / summary['patients']
summary = summary.sort_values('percentage', ascending=False)
summary.to_csv(OUT / 'histology_mutation_percentages.csv')
top = summary.head(3)
answer = '; '.join(f'{histology}: {row.percentage:.2f}% ({int(row.mutated_patients)}/{int(row.patients)} patients)' for histology, row in top.iterrows()) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(summary.to_string())
print(answer)
