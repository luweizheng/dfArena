import json
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')

clinical = pd.read_parquet(DATA / 'clinical/clinical_info.parquet',
                           columns=['Patient_description', 'histological_type'])
description = clinical['Patient_description'].astype('string')
selected = (description.str.contains('Breast invasive carcinoma', case=False, na=False)
            & description.str.contains(r'\bFEMALE\b', case=False, na=False))
patients = clinical.loc[selected].copy()
patients['barcode'] = patients.Patient_description.str.extract(r'\b(TCGA-[A-Z0-9]{2}-[A-Z0-9]{4})\b', expand=False)
assert patients.barcode.notna().all()
histology = patients.histological_type.astype('string').str.strip()
unknown = histology.isna() | histology.str.lower().isin(['', 'unknown', 'not available', 'not reported', 'none', 'na', 'n/a']) | histology.str.startswith('[', na=False)
patients = patients.loc[~unknown].copy()
assert not patients.barcode.duplicated().any()

mutations = pd.read_parquet(DATA / 'molecular/Mutation_Data.parquet',
                            columns=['ParticipantBarcode', 'Hugo_Symbol', 'FILTER'],
                            filters=[('Hugo_Symbol', '=', 'CDH1'), ('FILTER', '=', 'PASS')])
mutant_barcodes = mutations.loc[(mutations.Hugo_Symbol == 'CDH1') & (mutations.FILTER == 'PASS'), 'ParticipantBarcode'].drop_duplicates()
patients['CDH1_mutated'] = patients.barcode.isin(mutant_barcodes)
observed = pd.crosstab(patients.histological_type, patients.CDH1_mutated).reindex(columns=[False, True], fill_value=0)
observed.to_csv(OUT / 'contingency_before_filter.csv')
observed = observed.loc[observed.sum(axis=1) > 10, observed.sum(axis=0) > 10]
row_totals = observed.sum(axis=1)
column_totals = observed.sum(axis=0)
expected = pd.DataFrame({col: row_totals * total / row_totals.sum()
                         for col, total in column_totals.items()}, index=observed.index)
chi_square = ((observed - expected).pow(2) / expected).sum().sum()
observed.to_csv(OUT / 'contingency.csv')
expected.to_csv(OUT / 'expected.csv')
answer = f'Chi-square statistic: {chi_square:.6f} (df = {(observed.shape[0]-1)*(observed.shape[1]-1)}, N = {int(observed.to_numpy().sum())}).'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(observed.to_string())
print(answer)
