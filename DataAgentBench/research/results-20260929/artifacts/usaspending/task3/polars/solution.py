import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work/answer.json')

contracts = pl.read_parquet(DATA / 'contracts_db/contracts.parquet')
sectors = pl.read_parquet(DATA / 'agencies_db/naics_sectors.parquet')
# Observed NAICS representations are six digits, XX-XXXX, or naics-XXXXXX.
contracts = contracts.with_columns(
    pl.col('naics_code').str.to_lowercase().str.replace(r'^naics-', '')
    .str.replace_all('-', '').alias('canonical_naics'),
    pl.col('recipient_uei').str.to_uppercase().str.replace(r'^UEI:', '')
    .str.replace(r'-UEI$', '').alias('canonical_uei'),
)
assert contracts.filter(~pl.col('canonical_naics').str.contains(r'^\d{6}$')).height == 0
assert contracts.filter(~pl.col('canonical_uei').str.contains(r'^[A-Z0-9]{12}$')).height == 0
sector_codes = sectors.filter(pl.col('sector') == '33')['code'].to_list()
selected = contracts.filter(pl.col('canonical_naics').str.slice(0, 2).is_in(sector_codes))
count = selected.select(pl.col('canonical_uei').drop_nulls().n_unique()).item()
OUT.write_text(json.dumps({'answer': str(count)}) + '\n')
print(json.dumps({'matching_contracts': selected.height, 'answer': count}))
