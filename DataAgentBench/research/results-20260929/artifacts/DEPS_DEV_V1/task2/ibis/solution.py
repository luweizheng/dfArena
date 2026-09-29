import json
from pathlib import Path
import ibis

OUT = Path('/workspace/work')
con = ibis.duckdb.connect()
packages = con.read_parquet('/workspace/data/package/packageinfo.parquet')
mapping = con.read_parquet('/workspace/data/project/project_packageversion.parquet')
projects = con.read_parquet('/workspace/data/project/project_info.parquet')

# The serialized fields contain literal backslash-n sequences.
release_json = packages.VersionInfo.replace('\\n', '\n').cast('json')
releases = packages.filter((packages.System == 'NPM') & release_json['IsRelease'].cast('boolean')).select('System', 'Name', 'Version')
linked = releases.join(mapping.filter(mapping.ProjectType == 'GITHUB'), ['System', 'Name', 'Version']).select('ProjectName').distinct()
info = projects.Project_Information
direct_name = info.re_extract(r'([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', 1).nullif('')
organization = info.re_extract(r'under the organization ([A-Za-z0-9_-]+)', 1).nullif('')
repository = info.re_extract(r'The project ([A-Za-z0-9_.-]+) is', 1).nullif('')
name = ibis.coalesce(direct_name, organization + '/' + repository)
patterns = [r'(?i)\b([0-9][0-9,]*)\s+forks?\b', r'(?i)\bforks? count of\s+([0-9][0-9,]*)', r'(?i)\bforked\s+([0-9][0-9,]*)\s+times']
forks = ibis.coalesce(*[info.re_extract(p, 1).nullif('').replace(',', '').try_cast('int64') for p in patterns])
parsed = projects.mutate(ProjectName=name, ForkCount=forks)
missing = parsed.filter(parsed.ProjectName.isnull() | parsed.ForkCount.isnull()).select('Project_Information').to_pyarrow().to_pylist()
(OUT / 'unparsed.json').write_text(json.dumps(missing, indent=2))
if missing:
    raise ValueError(f'Unparsed project descriptions: {len(missing)}; see unparsed.json')
mit = parsed.filter(parsed.Licenses.replace('\\n', '\n').cast('json').cast('array<string>').contains('MIT'))
qualified = linked.join(mit, 'ProjectName').select('ProjectName', 'ForkCount').distinct()
ranked = qualified.group_by('ProjectName').aggregate(ForkCount=qualified.ForkCount.max()).order_by(ibis.desc('ForkCount'), 'ProjectName').limit(5)
rows = ranked.to_pyarrow().to_pylist()
(OUT / 'top_projects.json').write_text(json.dumps(rows, indent=2))
answer = '; '.join(f"{r['ProjectName']} ({r['ForkCount']:,} forks)" for r in rows) + '.'
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}))
print(answer)
