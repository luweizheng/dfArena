import json
from pathlib import Path
import polars as pl

DATA = Path('/workspace/data')
OUT = Path('/workspace/work')
keys = ['System', 'Name', 'Version']
packages = (
    pl.scan_parquet(DATA / 'package/packageinfo.parquet')
    .filter(pl.col('System') == 'NPM')
    .filter(pl.col('VersionInfo').str.json_path_match('$.IsRelease') == 'true')
    .select(keys).unique()
)
mappings = (
    pl.scan_parquet(DATA / 'project/project_packageversion.parquet')
    .filter(pl.col('ProjectType') == 'GITHUB')
    .join(packages, on=keys, how='semi')
    .select('ProjectName').unique()
)
s = pl.col('Project_Information')
projects = (
    pl.scan_parquet(DATA / 'project/project_info.parquet')
    .with_columns(
        pl.coalesce([
            s.str.extract(r'([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)'),
            pl.concat_str([
                s.str.extract(r'under the organization ([A-Za-z0-9_.-]+)'),
                s.str.extract(r'The project ([A-Za-z0-9_.-]+) is hosted'),
            ], separator='/'),
        ]).alias('ProjectName'),
        pl.coalesce([
            s.str.extract(r'([\d,]+) forks?\b'),
            s.str.extract(r'forks? count of ([\d,]+)'),
            s.str.extract(r'forked ([\d,]+) times'),
        ]).str.replace_all(',', '').cast(pl.Int64).alias('Forks'),
    ).collect()
)
assert projects['ProjectName'].null_count() == 0
assert projects['Forks'].null_count() == 0
eligible = (
    projects.lazy()
    .filter(pl.col('Licenses').str.json_decode(pl.List(pl.String)).list.contains('MIT'))
    .join(mappings, on='ProjectName', how='semi')
    .select('ProjectName', 'Forks').unique()
    .sort(['Forks', 'ProjectName'], descending=[True, False])
    .collect()
)
assert eligible['ProjectName'].n_unique() == eligible.height
result = eligible.head(5)
result.write_csv(OUT / 'top_projects.csv')
answer = '; '.join(f"{row['ProjectName']} ({row['Forks']:,} forks)" for row in result.to_dicts())
(OUT / 'answer.json').write_text(json.dumps({'answer': answer}) + '\n')
print(result)
