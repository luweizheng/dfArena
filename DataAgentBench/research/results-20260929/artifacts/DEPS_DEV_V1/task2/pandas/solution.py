import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')

def parse_json(value):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return json.loads(value.replace('\\n', '\n'))

packages = pd.read_parquet(ROOT / 'package/packageinfo.parquet', columns=['System', 'Name', 'Version', 'VersionInfo'])
packages = packages.loc[packages.System.eq('NPM')]
packages = packages.loc[packages.VersionInfo.map(lambda x: parse_json(x).get('IsRelease') is True)]
relations = pd.read_parquet(ROOT / 'project/project_packageversion.parquet')
matched = packages.merge(relations, on=['System', 'Name', 'Version'], how='inner')
eligible = matched.loc[matched.ProjectType.eq('GITHUB'), ['ProjectName']].drop_duplicates()
projects = pd.read_parquet(ROOT / 'project/project_info.parquet')
projects['ProjectName'] = projects.Project_Information.str.extract(r'([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', expand=False).str.rstrip('.,')

def forks(text):
    patterns = [r'([\d,]+)\s+forks?\b', r'forks? count of\s+([\d,]+)', r'forked\s+([\d,]+)\s+times']
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return int(match.group(1).replace(',', ''))
    raise ValueError('Unrecognized fork count: ' + text)

projects['Forks'] = projects.Project_Information.map(forks)
separate = projects.Project_Information.str.extract(r'The project ([A-Za-z0-9_.-]+) is hosted on GitHub under the organization ([A-Za-z0-9_.-]+)\.')
projects['ProjectName'] = projects.ProjectName.fillna(separate[1] + '/' + separate[0])
assert projects.ProjectName.notna().all()
projects = projects.loc[projects.Licenses.map(lambda x: 'MIT' in parse_json(x))]
ranked = projects.merge(eligible, on='ProjectName', how='inner')[['ProjectName', 'Forks']].drop_duplicates().sort_values(['Forks', 'ProjectName'], ascending=[False, True])
assert not ranked.ProjectName.duplicated().any()
ranked.to_csv(OUT / 'ranked_projects.csv', index=False)
top = ranked.head(5)
assert len(top) == 5
answer = '; '.join(f'{row.ProjectName} ({row.Forks:,} forks)' for row in top.itertuples(index=False)) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(top.to_string(index=False))
