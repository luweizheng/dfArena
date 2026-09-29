import json
import re
from datetime import date
from pathlib import Path
import polars as pl

OUT = Path('/workspace/work')
docs = pl.read_parquet('/workspace/data/domain_docs/files.parquet')
density_docs = docs.filter(pl.col('content').str.contains('Thermosphere neutral density'))
assert density_docs.height == 12
rows = []
for content in density_docs['content']:
    for line in content.splitlines():
        if re.match(r'^2024-\d{2}-\d{2}\s', line):
            fields = line.split()
            assert len(fields) == 9, fields
            rows.append((fields[0], fields[1], fields[2], fields[8]))
density = pl.DataFrame(rows, schema=['date', 'time', 'system', 'density'], orient='row').with_columns(
    pl.col('date').str.to_date(), pl.col('density').cast(pl.Float64).fill_nan(None)
).with_columns(pl.col('date').dt.month().alias('month'))
monthly = density.group_by('month').agg(pl.col('density').mean().alias('mean_density'), pl.len().alias('records')).sort('month')
assert monthly.height == 12
month = monthly.sort('mean_density', descending=True)['month'][0]
monthly.write_csv(OUT / 'monthly_density.csv')
assets = pl.scan_parquet('/workspace/data/domain_assets/files.parquet').filter(pl.col('file_description').str.contains('omni2_low_res_omni2_2024')).collect()
assert assets.height == 1
# Local OMNI2 format documentation defines word 39 as Kp, fill value 99.
raw = assets['content'][0].decode()
hourly = pl.DataFrame({'line': raw.splitlines()}).filter(pl.col('line').str.strip_chars() != '').with_columns(pl.col('line').str.extract_all(r'\S+').alias('fields')).select(
    pl.col('fields').list.get(0).cast(pl.Int32).alias('year'),
    pl.col('fields').list.get(1).cast(pl.Int32).alias('doy'),
    pl.col('fields').list.get(2).cast(pl.Int32).alias('hour'),
    pl.col('fields').list.get(38).cast(pl.Float64).alias('kp')
).with_columns((pl.date(pl.col('year'), 1, 1) + pl.duration(days=pl.col('doy')-1)).alias('date'))
selected = hourly.filter((pl.col('year') == 2024) & (pl.col('date').dt.month() == month) & (pl.col('kp') != 99))
mean_kp = selected['kp'].mean()
print(monthly)
print({'month': month, 'hours': selected.height, 'mean_kp_native': mean_kp, 'mean_kp_divided_by_10': mean_kp/10})
answer = f'{mean_kp:.4f} (OMNI2 encoded Kp units; {date(2024, month, 1):%B} 2024).'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
