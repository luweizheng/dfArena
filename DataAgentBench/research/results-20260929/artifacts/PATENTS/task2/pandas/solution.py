import json
import re
from pathlib import Path
import pandas as pd
from dateutil.parser import parse

OUT = Path('/workspace/work')
p = pd.read_parquet('/workspace/data/publication/publicationinfo.parquet', columns=['Patents_info', 'filing_date', 'grant_date', 'cpc'])
d = pd.read_parquet('/workspace/data/CPCDefinition/cpc_definition.parquet', columns=['symbol', 'level', 'titleFull', 'parents'])
# Publication country is encoded in the publication identifier, avoiding assignee-name matches.
p['publication'] = p.Patents_info.str.extract(r'(?:publication|pub\.)\s+(?:number|no\.)\s+([A-Z]{2}-[A-Za-z0-9-]+)', expand=False).str.rstrip('.')
assert p.publication.notna().all(), 'Unparsed publication identifier'
p = p[p.publication.str.startswith('DE-')].copy()
def natural_date(value):
    if not value or value == 'None Date':
        return pd.NaT
    clean = re.sub(r'(\d)(st|nd|rd|th)\b', r'\1', value)
    clean = re.sub(r'\b(dated|on|of|the)\b', '', clean)
    return pd.Timestamp(parse(clean))
p['grant'] = p.grant_date.map(natural_date)
p = p[p.grant.between('2019-07-01', '2019-12-31')].copy()
p['year'] = p.filing_date.map(natural_date).dt.year
assert p.year.notna().all()
def structured(value):
    if not value:
        return []
    return json.loads(value.replace('\\n', '\n'))
level4 = d[d.level.eq(4)].drop_duplicates('symbol').set_index('symbol')
def primary_groups(value):
    # Level-4 symbols in this table are the three-character CPC classes.
    return sorted({entry['code'][:3] for entry in structured(value) if entry.get('first') is True and entry['code'][:3] in level4.index})
p['group'] = p.cpc.map(primary_groups)
f = p[['publication', 'year', 'group']].explode('group').dropna(subset=['group']).drop_duplicates(['publication', 'group'])
counts = f.groupby(['group', 'year']).size().rename('filings')
series = []
peaks = []
for group, c in counts.groupby(level='group'):
    annual = c.droplevel('group').sort_index()
    annual = annual.reindex(range(int(annual.index.min()), int(annual.index.max()) + 1), fill_value=0)
    # Recursive EMA, initialized to the first annual count.
    ema = annual.ewm(alpha=0.1, adjust=False).mean()
    best = int(ema.idxmax())
    peaks.append({'group': group, 'title': level4.loc[group, 'titleFull'].strip(), 'best_year': best, 'peak_ema': float(ema.loc[best])})
    series.extend({'group': group, 'year': int(y), 'filings': int(annual.loc[y]), 'ema': float(ema.loc[y])} for y in annual.index)
result = pd.DataFrame(peaks).sort_values(['peak_ema','group'], ascending=[False,True])
result.to_csv(OUT / 'peaks.csv', index=False)
pd.DataFrame(series).to_csv(OUT / 'annual_ema.csv', index=False)
answer = 'Peak filing-year EMA (alpha=0.1; initialized to first annual count): ' + '; '.join(f"{r.group} — {r.title} — {r.best_year}" for r in result.itertuples()) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}, ensure_ascii=False), encoding='utf-8')
print('Eligible German publications:', len(p), 'Groups:', len(result))
print(result.to_string(index=False))
