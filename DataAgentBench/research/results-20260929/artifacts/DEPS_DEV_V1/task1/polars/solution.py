import json
from pathlib import Path
import polars as pl

ROOT = Path('/workspace/data')
OUT = Path('/workspace/work')
p = (pl.read_parquet(ROOT/'package/packageinfo.parquet')
     .filter(pl.col('System') == 'NPM')
     .with_columns(pl.col('VersionInfo').str.json_decode(pl.Struct({'IsRelease':pl.Boolean,'Ordinal':pl.Int64})).alias('meta')))
releases = p.filter(pl.col('meta').struct.field('IsRelease') == True)
# Release versions are ordered numerically by semantic version, not publication time.
assert releases.filter(pl.col('Version').str.contains('-')).height == 0
releases = releases.with_columns([
    pl.col('Version').str.extract(r'^v?(\d+)\.(\d+)\.(\d+)', i+1).cast(pl.Int64).alias(c)
    for i,c in enumerate(['major','minor','patch'])
])
latest = (releases.sort(['Name','major','minor','patch','Version'])
          .unique(subset=['System','Name'],keep='last')
          .select('System','Name','Version'))
projects = pl.read_parquet(ROOT/'project/project_info.parquet')
s = pl.col('Project_Information')
projects = projects.with_columns(
    pl.coalesce(s.str.extract(r'([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)'), pl.concat_str([s.str.extract(r'organization ([A-Za-z0-9_.-]+)').str.strip_chars_end('.'), s.str.extract(r'The project ([A-Za-z0-9_.-]+)')], separator='/')).str.strip_chars_end('.').alias('ProjectName'),
    pl.coalesce(s.str.extract(r'(?i)([\d,]+) stars?\b'),
                s.str.extract(r'(?i)stars? count of ([\d,]+)'), s.str.extract(r'(?i)starred by ([\d,]+)')).str.replace_all(',','').cast(pl.Int64).alias('Stars')
)
missing = projects.filter(pl.col('ProjectName').is_null() | pl.col('Stars').is_null())
assert missing.height == 0, missing.select('Project_Information').to_dicts()
mapping = pl.read_parquet(ROOT/'project/project_packageversion.parquet').filter(pl.col('ProjectType') == 'GITHUB')
ranked = (latest.join(mapping,on=['System','Name','Version'])
          .join(projects.select('ProjectName','Stars'),on='ProjectName')
          .group_by('Name','Version').agg(pl.col('Stars').max())
          .sort(['Stars','Name'],descending=[True,False]))
top = ranked.head(5)
assert top.height == 5
ranked.write_csv(OUT/'ranking.csv')
answer = '; '.join(f"{r['Name']} {r['Version']} ({r['Stars']:,} GitHub stars)" for r in top.to_dicts()) + '.'
(OUT/'answer.json').write_text(json.dumps({'answer':answer})+'\n')
print(answer)
