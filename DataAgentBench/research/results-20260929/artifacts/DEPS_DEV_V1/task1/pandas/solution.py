import json
import re
from pathlib import Path
import pandas as pd

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
packages = pd.read_parquet(DATA / 'package/packageinfo.parquet', columns=['System', 'Name', 'Version', 'VersionInfo'])
packages = packages.loc[packages.System.eq('NPM')].copy()
packages['release'] = packages.VersionInfo.str.contains(r'"IsRelease":\s*true', regex=True)
releases = packages.loc[packages.release].copy()

def version_key(version):
    # NPM SemVer ordering: numeric core, then prerelease identifiers; ignore build metadata.
    match = re.fullmatch(r'[v=]?(\d+)\.(\d+)\.(\d+)(?:-([^+]+))?(?:\+.*)?', version)
    if not match:
        raise ValueError(f'Unexpected release version: {version}')
    major, minor, patch, pre = match.groups()
    pre_key = tuple((0, int(p)) if p.isdigit() else (1, p) for p in pre.split('.')) if pre else ()
    return (int(major), int(minor), int(patch), pre is None, pre_key)

releases['version_order'] = releases.Version.map(version_key)
latest = releases.sort_values(['Name', 'version_order', 'Version']).drop_duplicates(['System', 'Name'], keep='last')
mappings = pd.read_parquet(DATA / 'project/project_packageversion.parquet')
mappings = mappings.loc[mappings.ProjectType.eq('GITHUB')].drop_duplicates()
projects = pd.read_parquet(DATA / 'project/project_info.parquet')
s = projects.Project_Information
projects['ProjectName'] = s.str.extract(r'([\w.-]+/[\w.-]+)')[0]
missing = projects.ProjectName.isna()
parts = s.loc[missing].str.extract(r'project ([\w.-]+).*?organization ([\w.-]+)')
projects.loc[missing, 'ProjectName'] = parts[1] + '/' + parts[0]
stars = s.str.extract(r'([\d,]+) stars?\b')[0].fillna(s.str.extract(r'stars? count of ([\d,]+)')[0])
stars = stars.fillna(s.str.extract(r'starred by ([\d,]+) users')[0])
assert projects.ProjectName.notna().all(), s[projects.ProjectName.isna()].tolist()
assert stars.notna().all(), s[stars.isna()].tolist()
projects['Stars'] = pd.to_numeric(stars.str.replace(',', '', regex=False))
joined = latest.merge(mappings, on=['System', 'Name', 'Version'], how='inner').merge(projects[['ProjectName', 'Stars']], on='ProjectName', how='inner')
# A package may have multiple relationship records; rank each distinct package once.
ranked = joined.sort_values(['Stars', 'Name', 'ProjectName'], ascending=[False, True, True]).drop_duplicates(['System', 'Name'])
top = ranked.head(5)
ranked[['Name', 'Version', 'ProjectName', 'Stars']].to_csv(OUT / 'ranked_packages.csv', index=False)
answer = '; '.join(f'{r.Name} {r.Version} ({r.Stars:,} GitHub stars)' for r in top.itertuples()) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(top[['Name', 'Version', 'ProjectName', 'Stars']].to_string(index=False))
print(f'Release rows: {len(releases)}; distinct latest releases: {len(latest)}; ranked packages: {len(ranked)}')
