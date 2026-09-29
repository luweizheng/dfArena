import csv
import io
import json
from pathlib import Path
import ibis
import pyarrow as pa

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
ibis.set_backend(con)
docs = con.read_parquet('/workspace/data/domain_docs/files.parquet')
assets = con.read_parquet('/workspace/data/domain_assets/files.parquet')
# Decode the embedded TSV representation; relational operations remain in Ibis.
texts = docs.filter(docs.content.contains('1 58214U')).to_pyarrow().to_pylist()
records = []
for item in texts:
    records.extend(csv.DictReader(io.StringIO(item['content'].split('\n', 1)[1]), delimiter='\t'))
obs = ibis.memtable(pa.table({'TLE_LINE1': [r['TLE_LINE1'] for r in records], 'Epoch Info': [r['Epoch Info'] for r in records]}))

def epoch_date(line):
    yy = line.substr(18, 2).cast('int32')
    year = ibis.ifelse(yy < 57, yy + 2000, yy + 1900)
    jan1 = (year.cast('string') + '-01-01').cast('date')
    days = line.substr(20, 3).cast('int32') - 1
    return (jan1 + days.as_interval("D")).cast('date')

obs = obs.mutate(norad=obs.TLE_LINE1.substr(2, 5), date=epoch_date(obs.TLE_LINE1))
# Positive storm descriptions exclude the separately described quiet observations.
storm_terms = r'disturbed geomagnetic|heightened geomagnetic|elevated auroral|energetic particle|elevated geomagnetic|geomagnetic unrest|active geomagnetic|severe space weather'
storm = obs.filter((obs.norad == '58214') & obs['Epoch Info'].re_search(storm_terms) & ~obs['Epoch Info'].contains('undisturbed'))
period = storm.aggregate(start=storm.date.min(), end=storm.date.max())

blobs = assets.filter(assets.file_description.contains('TLE_43180')).select('content').to_pyarrow().to_pylist()
lines = [line for blob in blobs for line in blob['content'].decode('utf-8').splitlines()]
tle = ibis.memtable(pa.table({'line': lines}))
tle = tle.filter(tle.line.startswith('1 43180'))
# TLE columns 54-61: sign, five mantissa digits, signed one-digit exponent.
tle = tle.mutate(date=epoch_date(tle.line), bstar=(
    ibis.ifelse(tle.line.substr(53, 1) == '-', -1.0, 1.0)
    * tle.line.substr(54, 5).cast('float64') / 100000
    * (ibis.literal(10.0) ** tle.line.substr(59, 2).cast('int32'))
))
selected = tle.cross_join(period).filter(lambda t: t.date.between(t.start, t.end))
result = selected.aggregate(mean_bstar=selected.bstar.mean(), count=selected.count()).to_pyarrow().to_pylist()[0]
assert result['count'] > 0
answer = {'answer': f"{result['mean_bstar']:.6f}"}
(OUT / 'answer.json').write_text(json.dumps(answer) + '\n')
print(period.to_pyarrow().to_pylist())
print(result)
print(json.dumps(answer))
