import json
from pathlib import Path
import pandas as pd

OUT = Path('/workspace/work')

def parse_structured(value):
    if value is None or not value.strip():
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return json.loads(value.replace('\\n', '\n'))

def main():
    definitions = pd.read_parquet('/workspace/data/CPCDefinition/cpc_definition.parquet', columns=['symbol', 'level', 'parents'])
    level5 = set(definitions.loc[definitions['level'].eq(5), 'symbol'])
    code_groups = {}
    for row in definitions.itertuples(index=False):
        groups = ({row.symbol} | set(parse_structured(row.parents))) & level5
        code_groups[row.symbol] = groups
    patents = pd.read_parquet('/workspace/data/publication/publicationinfo.parquet', columns=['filing_date', 'cpc'])
    patents['year'] = pd.to_numeric(patents['filing_date'].str.extract(r'\b(\d{4})\b', expand=False), errors='coerce').astype('Int64')
    def primary_groups(value):
        groups = set()
        for entry in parse_structured(value):
            if entry.get('first') is True:
                code = entry['code']
                groups.update(code_groups.get(code, {code[:4]} & level5))
        return sorted(groups)
    patents['group'] = patents['cpc'].map(primary_groups)
    filings = patents[['year', 'group']].explode('group').dropna()
    filings['year'] = filings['year'].astype(int)
    counts = filings.groupby(['group', 'year']).size().rename('filings')
    annual_frames = []
    peaks = []
    for group, series in counts.groupby(level='group'):
        series = series.droplevel('group').sort_index()
        series = series.reindex(range(int(series.index.min()), int(series.index.max()) + 1), fill_value=0)
        # Standard recursive EMA: initial EMA is the first annual count;
        # subsequent EMA = 0.2 * count + 0.8 * previous EMA.
        ema = series.ewm(alpha=0.2, adjust=False).mean()
        best_year = int(ema.idxmax())  # sorted index gives earliest tied year
        peaks.append({'group': group, 'best_year': best_year, 'peak_ema': float(ema.loc[best_year])})
        annual_frames.append(pd.DataFrame({'group': group, 'year': series.index, 'filings': series.values, 'ema': ema.values}))
    peaks = pd.DataFrame(peaks).sort_values('group')
    result = peaks.loc[peaks.best_year.eq(2022), 'group'].tolist()
    pd.concat(annual_frames, ignore_index=True).to_csv(OUT / 'annual_ema.csv', index=False)
    peaks.to_csv(OUT / 'group_peaks.csv', index=False)
    (OUT / 'answer.json').write_text(json.dumps({'answer': ', '.join(result)}) + '\n')
    print('Publications:', len(patents), 'Missing filing years:', int(patents.year.isna().sum()))
    print('Level-5 groups with primary filings:', len(peaks))
    print(json.dumps({'answer': ', '.join(result)}))

if __name__ == '__main__':
    main()
