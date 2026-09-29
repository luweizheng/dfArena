import io
import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace')
docs = pd.read_parquet(ROOT / 'data/domain_docs/files.parquet')
frames = []
for content in docs['content']:
    if 'Density derived from GPS accelerations (kg/m3)' not in content:
        continue
    start = re.search(r'^2024-\d{2}-\d{2}\s', content, re.M)
    if start is None:
        continue
    frame = pd.read_csv(io.StringIO('\n'.join(re.findall(r'^2024-\d{2}-\d{2}[^\n]*', content, re.M))), sep=r'\s+', header=None,
                        usecols=[0, 1, 8], names=['date', 'time', 'density'])
    frame['month'] = pd.to_datetime(frame['date']).dt.to_period('M')
    frames.append(frame)
assert len(frames) == 12, len(frames)
density = pd.concat(frames, ignore_index=True)
assert not density.duplicated(['date', 'time']).any()
monthly = density.groupby('month')['density'].agg(['mean', 'count', 'min', 'max'])
assert len(monthly) == 12
peak = monthly['mean'].idxmax()
print(monthly.to_string())
assets = pd.read_parquet(ROOT / 'data/domain_assets/files.parquet')
selected = assets.loc[assets.file_description.str.contains('omni2_low_res_omni2_2024', case=False), 'content']
assert len(selected) == 1
omni = pd.read_csv(io.BytesIO(selected.iloc[0]), sep=r'\s+', header=None)
# Local OMNI2 format documentation: words 1,2,3 = year, day of year, hour;
# word 39 = Kp (99 is fill), encoded e.g. 4 = 40, 3+ = 33.
timestamps = pd.to_datetime(omni[0].astype(str), format='%Y') + pd.to_timedelta(omni[1]-1, unit='D') + pd.to_timedelta(omni[2], unit='h')
kp = omni.loc[timestamps.dt.to_period('M').eq(peak), 38]
kp = kp.mask(kp.eq(99))
mean_encoded = kp.mean()
print('Peak month:', peak, 'hours:', len(kp), 'valid:', kp.count(), 'mean encoded:', mean_encoded)
answer = f'{mean_encoded:.4f} in OMNI2’s stored Kp units (Kp × 10), equivalent to {mean_encoded / 10:.4f} Kp, for {peak.strftime("%B %Y")}.'
(ROOT / 'work/answer.json').write_text(json.dumps({'answer': answer}) + '\n')
monthly.to_csv(ROOT / 'work/monthly_density.csv')
