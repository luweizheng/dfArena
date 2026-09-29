import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    languages = con.read_parquet('/workspace/data/metadata/languages.parquet')
    licenses = con.read_parquet('/workspace/data/metadata/licenses.parquet')
    commits = con.read_parquet('/workspace/data/artifacts/commits.parquet')

    # Shell can be any listed language, not necessarily the primary language.
    shell_repos = languages.filter(
        languages.language_description.re_search(r'\bShell\s*\(')
    ).select('repo_name')
    apache_repos = licenses.filter(
        licenses.license.lower() == 'apache-2.0'
    ).select('repo_name')
    # Semijoins preserve commit records without multiplying them by metadata rows.
    eligible = commits.semi_join(shell_repos, 'repo_name').semi_join(apache_repos, 'repo_name')
    message = eligible.message
    qualifying = eligible.filter(
        message.notnull(),
        message.length() < 1000,
        ~message.lower().startswith('merge'),
        ~message.lower().startswith('update'),
        ~message.lower().startswith('test'),
    )
    count = int(qualifying.count().execute())
    output = {'answer': f'{count:,} commit messages.'}
    Path('/workspace/work/answer.json').write_text(json.dumps(output) + '\n')
    print(json.dumps(output))


if __name__ == '__main__':
    main()
