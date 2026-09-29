import json
from pathlib import Path
import ibis
import pyarrow as pa

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
docs = con.read_parquet('/workspace/data/domain_docs/files.parquet')
assets = con.read_parquet('/workspace/data/domain_assets/files.parquet')
# These twelve documents describe the Swarm-B GPS-derived densities.
swarm_docs = docs.filter(docs.content.substr(0, 180).contains('Thermosphere neutral density'))
lines = swarm_docs.select(line=swarm_docs.content.split('\n').unnest())
lines = lines.filter(lines.line.re_search(r'^2024-\d{2}-\d{2}\s'))
fields = lines.line.strip().re_replace(r'\s+', ' ').split(' ')
density = lines.select(date=fields[0].cast('date'), density=fields[8].try_cast('float64'))
density = density.filter(density.density.notnull() & ~density.density.isnan())
monthly = density.group_by(month=density.date.month()).aggregate(mean_density=density.density.mean(), n=density.count()).order_by(ibis.desc('mean_density'))
ranked = monthly.to_pyarrow().to_pylist()
print('Monthly density ranking:', ranked)
assert len(ranked) == 12
month = ranked[0]['month']
# Decode the binary text representation, leaving parsing and computation to Ibis.
blobs = assets.filter(assets.file_description.contains('omni2_low_res_omni2_2024')).select('content').to_pyarrow().to_pylist()
assert len(blobs) == 1
raw = ibis.memtable(pa.table({'payload': [blobs[0]['content'].decode('utf-8')]}))
rows = raw.select(line=raw.payload.split('\n').unnest())
rows = rows.filter(rows.line.strip().re_search(r'^2024\s'))
f = rows.line.strip().re_replace(r'\s+', ' ').split(' ')
# Standard OMNI2 hourly format: year, day of year, hour; Kp is column 39.
omni = rows.select(year=f[0].cast('int32'), doy=f[1].cast('int32'), hour=f[2].cast('int32'), kp=f[38].cast('float64'))
omni = omni.mutate(date=ibis.date(2024, 1, 1) + (omni.doy - 1).as_interval('D'))
selected = omni.filter((omni.date.month() == month) & (omni.kp != 99))
stats = con.to_pyarrow(selected.aggregate(mean_kp=selected.kp.mean(), hours=selected.count())).to_pylist()[0]
print('Selected month and OMNI2 statistics:', month, stats)
(OUT / 'answer.json').write_text(json.dumps({'answer': f"{stats['mean_kp']:.4f}"}) + '\n')
(OUT / 'calculation.json').write_text(json.dumps({'monthly_density': ranked, 'selected_month': month, 'omni': stats}, indent=2) + '\n')

if __name__ == '__main__':
    pass
