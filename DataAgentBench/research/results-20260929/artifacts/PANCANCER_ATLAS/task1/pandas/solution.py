import json
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
clinical = pd.read_parquet(DATA / 'clinical/clinical_info.parquet', columns=['Patient_description', 'icd_o_3_histology'])
lgg = clinical.loc[clinical['Patient_description'].str.contains('Brain lower grade glioma', case=False, na=False)].copy()
lgg['ParticipantBarcode'] = lgg['Patient_description'].str.extract(r'(TCGA-[A-Za-z0-9]{2}-[A-Za-z0-9]{4})', expand=False)
histology = lgg['icd_o_3_histology'].str.strip()
lgg = lgg.loc[histology.notna() & histology.ne('') & ~histology.str.fullmatch(r'\[.*\]', na=False)].copy()
assert lgg['ParticipantBarcode'].notna().all()
assert not lgg['ParticipantBarcode'].duplicated().any()
expression = pd.read_parquet(DATA / 'molecular/RNASeq_Expression.parquet', filters=[('Symbol', '=', 'IGF2')], columns=['ParticipantBarcode', 'SampleBarcode', 'normalized_count'])
expression['normalized_count'] = pd.to_numeric(expression['normalized_count'], errors='coerce')
expression = expression.loc[np.isfinite(expression['normalized_count']) & expression['normalized_count'].ge(0)].copy()
joined = expression.merge(lgg[['ParticipantBarcode', 'icd_o_3_histology']], on='ParticipantBarcode', how='inner', validate='many_to_one')
joined['log10_expression'] = np.log10(joined['normalized_count'] + 1)
summary = joined.groupby('icd_o_3_histology')['log10_expression'].agg(['mean', 'count']).sort_index()
assert not summary.empty
summary.to_csv(OUT / 'histology_summary.csv')
answer = 'Mean log10(IGF2 normalized_count + 1) for LGG by ICD-O-3 histology: ' + '; '.join(f'{code}: {row["mean"]:.6f}' for code, row in summary.iterrows()) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(summary.to_string())
print(answer)
print(f'Included {len(joined)} samples from {joined.ParticipantBarcode.nunique()} patients.')
