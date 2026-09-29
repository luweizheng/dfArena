import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
clinical = con.read_parquet('/workspace/data/clinical/clinical_info.parquet')
mutations = con.read_parquet('/workspace/data/molecular/Mutation_Data.parquet')
description = clinical.Patient_description
histology = clinical.histological_type
cohort = clinical.filter(
    description.lower().contains('breast invasive carcinoma'),
    description.re_search(r'\bFEMALE\b'),
    histology.notnull(),
    histology.strip() != '',
    ~histology.strip().lower().isin(['[not available]', '[not evaluated]', '[unknown]', 'unknown', 'not available', 'not reported']),
).select(
    barcode=description.re_extract(r'(TCGA-[A-Za-z0-9]{2}-[A-Za-z0-9]{4})', 1),
    histology=histology,
).distinct()
positive = mutations.filter(
    mutations.Hugo_Symbol == 'CDH1', mutations.FILTER == 'PASS'
).select(barcode=mutations.ParticipantBarcode).distinct().mutate(mutated=True)
patients = cohort.left_join(positive, 'barcode').select(
    cohort.barcode, cohort.histology, mutated=positive.mutated.fill_null(False)
)
counts = patients.group_by('histology').aggregate(
    present=patients.mutated.cast('int64').sum(), total=patients.count()
)
# Include zero-count cells explicitly and filter both dimensions by their margins.
cells = counts.select('histology', status=ibis.literal('present'), observed=counts.present).union(
    counts.select('histology', status=ibis.literal('absent'), observed=counts.total-counts.present)
)
row_margins = cells.group_by('histology').aggregate(row_total=cells.observed.sum())
col_margins = cells.group_by('status').aggregate(col_total=cells.observed.sum())
retained = cells.join(row_margins.filter(row_margins.row_total > 10), 'histology').join(
    col_margins.filter(col_margins.col_total > 10), 'status'
).select('histology', 'status', 'observed')
# Recompute expected frequencies after the exclusions.
final_cells = retained.mutate(
    row_total=retained.observed.sum().over(ibis.window(group_by='histology')),
    col_total=retained.observed.sum().over(ibis.window(group_by='status')),
    grand_total=retained.observed.sum().over(ibis.window()),
)
final_cells = final_cells.mutate(expected=final_cells.row_total*final_cells.col_total/final_cells.grand_total)
final_cells = final_cells.mutate(contribution=(final_cells.observed-final_cells.expected)**2/final_cells.expected)
statistic = float(final_cells.contribution.sum().execute())
audit = final_cells.order_by('histology','status').to_pyarrow().to_pylist()
(OUT/'contingency.json').write_text(json.dumps(audit, indent=2))
answer = {'answer': f'The Pearson chi-square statistic is χ² = {statistic:.4f}.'}
(OUT/'answer.json').write_text(json.dumps(answer, ensure_ascii=False))
print(json.dumps(answer, ensure_ascii=False))
print(json.dumps(audit, indent=2))
