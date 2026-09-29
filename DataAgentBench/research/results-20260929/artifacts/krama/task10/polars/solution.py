import io
import json
from datetime import datetime, timedelta
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
docs = pl.read_parquet(DATA / 'domain_docs/files.parquet')
orbital_docs = docs.filter(pl.col('content').str.contains('CCSDS_OMM_VERS') & pl.col('content').str.contains('58214'))
tables = []
for content in orbital_docs['content']:
    start = content.index('CCSDS_OMM_VERS')
    tables.append(pl.read_csv(io.StringIO(content[start:]), separator='\t', infer_schema=False))
observations = pl.concat(tables)
quiet = r'(?i)benign|baseline|calm|subdued|minimal|stability|undisturbed|low-flux'
storm = observations.filter(pl.col('TLE_LINE1').str.starts_with('1 58214') & ~pl.col('Epoch Info').str.contains(quiet))

def epoch(value):
    year = int(value[:2])
    year += 2000 if year < 57 else 1900
    return datetime(year, 1, 1) + timedelta(days=float(value[2:]) - 1)

storm = storm.with_columns(pl.col('TLE_LINE1').str.slice(18, 14).map_elements(epoch, return_dtype=pl.Datetime('us')).alias('epoch'))
start_date, end_date = storm.select(pl.col('epoch').min().dt.date().alias('start'), pl.col('epoch').max().dt.date().alias('end')).row(0)
assets = pl.read_parquet(DATA / 'domain_assets/files.parquet').filter(pl.col('file_description').str.contains('43180'))
lines = [line for content in assets['content'] for line in content.decode('utf-8').splitlines() if line.startswith('1 43180')]
tle = pl.DataFrame({'line': lines}).with_columns(
    pl.col('line').str.slice(18, 14).map_elements(epoch, return_dtype=pl.Datetime('us')).alias('epoch'),
    pl.col('line').str.slice(53, 8).str.strip_chars().alias('compact'),
)
tle = tle.with_columns((
    pl.col('compact').str.extract(r'^([+-]?\d{5})', 1).cast(pl.Float64) * 1e-5
    * pl.lit(10.0).pow(pl.col('compact').str.extract(r'([+-]\d)$', 1).cast(pl.Int32))
).alias('bstar'))
selected = tle.filter(pl.col('epoch').dt.date().is_between(start_date, end_date))
assert selected.height > 0 and selected['bstar'].null_count() == 0
mean = selected.select(pl.col('bstar').mean()).item()
selected.write_csv(OUT / 'selected_tle.csv')
print(f'Storm dates: {start_date} through {end_date}; TLE records: {selected.height}; mean BSTAR: {mean:.12f}')
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{mean:.6f}'}) + '\n')

if __name__ == '__main__':
    pass
