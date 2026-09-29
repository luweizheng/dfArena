import json
from pathlib import Path
import ibis


def main():
    con = ibis.duckdb.connect()
    languages = con.read_parquet('/workspace/data/metadata/languages.parquet')
    files = con.read_parquet('/workspace/data/artifacts/files.parquet')
    contents = con.read_parquet('/workspace/data/artifacts/contents.parquet')

    # Require known language metadata and exclude any repository listing Python.
    python_repos = languages.filter(
        languages.language_description.lower().contains('python')
    ).select('repo_name').distinct()
    non_python_repos = languages.filter(
        languages.language_description.notnull()
    ).select('repo_name').distinct().anti_join(python_repos, 'repo_name')

    # Match the specified filename at any directory depth. Blob IDs link actual
    # file occurrences to available text, regardless of the sampled repository.
    readmes = files.filter(files.path.re_search(r'(^|/)README\.md$'))
    available = (
        readmes.semi_join(non_python_repos, 'repo_name')
        .inner_join(contents.filter(contents.content.notnull()), 'id')
    )
    counts = available.aggregate(
        total=available.count(),
        with_copyright=available.content.lower().contains('copyright').sum(),
    ).to_pyarrow().to_pylist()[0]
    total = counts['total']
    matching = counts['with_copyright']
    if not total:
        answer = 'No eligible README.md files have available contents.'
    else:
        answer = f'{matching / total:.2%} ({matching} of {total} README.md files with available contents).'
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': answer}) + '\n')
    print(json.dumps(counts))
    print(answer)


if __name__ == '__main__':
    main()
