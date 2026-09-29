import io
import json
import re
from pathlib import Path
import pandas as pd

OUT = Path('/workspace/work')
docs = pd.read_parquet('/workspace/data/domain_docs/files.parquet')
observations = []
for content in docs['content']:
    if 'TLE_LINE1' in content and '58214' in content:
        lines = content.splitlines()
        header = next(i for i, line in enumerate(lines) if 'TLE_LINE1' in line and 'Epoch Info' in line)
        observations.append(pd.read_csv(io.StringIO('\n'.join(lines[header:])), sep='\t'))
obs = pd.concat(observations, ignore_index=True)
obs = obs.loc[obs['TLE_LINE1'].str.match(r'1 58214', na=False)].copy()

def epoch(value):
    year = int(value[:2])
    year += 2000 if year < 57 else 1900
    return pd.Timestamp(year=year, month=1, day=1) + pd.to_timedelta(float(value[2:]) - 1, unit='D')

obs['epoch'] = obs['TLE_LINE1'].str.slice(18, 32).map(epoch)
# Calm/baseline descriptions distinguish the early-May observations from the storm.
calm = r'benign|baseline|subdued|minimal|stability|undisturbed|low-flux|calm|quiet'
storm = obs.loc[~obs['Epoch Info'].str.contains(calm, case=False, regex=True)]
start = storm['epoch'].min().normalize()
end = storm['epoch'].max().normalize() + pd.Timedelta(days=1)
assets = pd.read_parquet('/workspace/data/domain_assets/files.parquet')
rows = []
for blob in assets.loc[assets['file_description'].str.contains(r'\bTLE_43180\b', na=False), 'content']:
    for line in blob.decode('utf-8').splitlines():
        if line.startswith('1 43180'):
            value = line[53:61].strip()
            m = re.fullmatch(r'([+-]?)(\d{5})([+-]\d)', value)
            assert m, value
            bstar = (-1 if m[1] == '-' else 1) * float('0.' + m[2]) * 10 ** int(m[3])
            rows.append({'epoch': epoch(line[18:32]), 'bstar': bstar})
tle = pd.DataFrame(rows)
selected = tle.loc[tle['epoch'].ge(start) & tle['epoch'].lt(end)]
assert not selected.empty
mean = selected['bstar'].mean()
selected.to_csv(OUT / 'selected_tle.csv', index=False)
print(f'Storm dates: {start.date()} through {(end-pd.Timedelta(days=1)).date()}; TLE records: {len(selected)}; mean BSTAR: {mean:.12f}')
(OUT / 'answer.json').write_text(json.dumps({'answer': f'{mean:.6f}'}) + '\n')

if __name__ == '__main__':
    pass
