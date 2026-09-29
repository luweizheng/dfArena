import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
c = ibis.duckdb.connect()
p = c.read_parquet('/workspace/data/package/packageinfo.parquet')
m = c.read_parquet('/workspace/data/project/project_packageversion.parquet')
g = c.read_parquet('/workspace/data/project/project_info.parquet')
# Stable NPM releases are ordered by their numeric SemVer components.
p = p.filter((p.System == 'NPM') & p.VersionInfo.cast('json')['IsRelease'].cast('boolean'))
p = p.select('System', 'Name', 'Version', ordinal=p.VersionInfo.cast('json')['Ordinal'].cast('int64')).distinct()
p = p.mutate(**{part: p.Version.re_extract(r'^v?(\d+)\.(\d+)\.(\d+)', i).try_cast('int64') for i, part in enumerate(['major', 'minor', 'patch'], 1)})
assert p.filter(p.major.isnull()).count().execute() == 0, 'Unexpected release version syntax'
w = ibis.window(group_by=['System', 'Name'], order_by=[ibis.desc('major'), ibis.desc('minor'), ibis.desc('patch'), ibis.desc('ordinal')])
latest = p.mutate(rn=ibis.row_number().over(w)).filter(lambda t: t.rn == 0).select('System', 'Name', 'Version')
s = g.Project_Information
stars_before = s.re_extract(r'(?i)([0-9,]+) stars?\b', 1).replace(',', '').try_cast('int64')
stars_after = s.re_extract(r'(?i)stars? count of ([0-9,]+)', 1).replace(',', '').try_cast('int64')
repo = s.re_extract(r'([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', 1)
org = s.re_extract(r'under the organization ([A-Za-z0-9_-]+)', 1)
name = s.re_extract(r'The project ([A-Za-z0-9_.-]+) is hosted', 1)
repo = (repo == '').ifelse(org + '/' + name, repo)
starred = s.re_extract(r'starred by ([0-9,]+) users', 1).replace(',', '').try_cast('int64')
g = g.select(ProjectName=repo, stars=stars_before.coalesce(stars_after, starred), description=s)
missing = g.filter(g.stars.isnull() | (g.ProjectName == '')).to_pyarrow().to_pylist()
(OUT / 'unparsed_projects.json').write_text(json.dumps(missing, indent=2))
assert not missing, 'Unparsed project metrics'
m = m.filter((m.System == 'NPM') & (m.ProjectType == 'GITHUB'))
j = latest.join(m, ['System', 'Name', 'Version']).join(g, 'ProjectName')
ranked = j.group_by('Name', 'Version').aggregate(stars=j.stars.max()).order_by(ibis.desc('stars'), 'Name').limit(5)
rows = ranked.to_pyarrow().to_pylist()
(OUT / 'top_packages.json').write_text(json.dumps(rows, indent=2))
answer = '; '.join(f"{r['Name']} {r['Version']} ({r['stars']:,} GitHub stars)" for r in rows) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(answer)
