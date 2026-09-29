"""Count KEV CVEs with non-English descriptions and no English description.

All relational work runs lazily through Ibis/DuckDB. Python scalar UDFs
handle reversible JSON parsing and the heterogeneous identifier encodings.
"""
import json
from pathlib import Path
import ibis
from decoder import candidates

@ibis.udf.scalar.python
def decoded_ids(value: str) -> list[str]:
    return sorted(candidates(value)) if value is not None else []

@ibis.udf.scalar.python
def languages(value: str) -> list[str]:
    return [entry['lang'].lower() for entry in json.loads(value or '[]') if entry.get('lang')]


def main():
    con = ibis.duckdb.connect()
    docs = con.read_parquet('/workspace/data/descriptions_db/cve_documents.parquet')
    kev = con.read_parquet('/workspace/data/kev_db/kev_entries.parquet')
    # KEV notes contain an explicit NVD detail URL for the catalog entry itself.
    # Unlike other links in notes, this identifies the listed CVE unambiguously.
    kev = kev.mutate(canonical=kev.notes.re_extract(r'nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)', 1),
                     candidates=decoded_ids(kev.cve_ref))
    assert kev.filter(kev.canonical.isnull() | (kev.canonical == '')).count().execute() == 0
    assert kev.filter(~kev.candidates.contains(kev.canonical)).count().execute() == 0
    catalog = kev.select('canonical').distinct()
    docs = docs.mutate(candidates=decoded_ids(docs.cve), langs=languages(docs.descriptions))
    assert docs.filter(docs.candidates.length() == 0).count().execute() == 0
    expanded = docs.mutate(canonical=docs.candidates.unnest())
    matched = expanded.semi_join(catalog, 'canonical')
    # Some noise fragments admit more than one decoding. Verify that no such
    # document can possibly refer to a KEV CVE, so they cannot affect this answer.
    assert matched.filter(matched.candidates.length() != 1).count().execute() == 0
    flags = matched.mutate(has_en=matched.langs.contains('en'),
                           has_other=matched.langs.filter(lambda x: x != 'en').length() > 0)
    per_cve = flags.group_by('canonical').aggregate(has_en=flags.has_en.any(),
                                                   has_other=flags.has_other.any())
    result = per_cve.filter(~per_cve.has_en & per_cve.has_other).count()
    count = int(result.execute())
    Path('/workspace/work/answer.json').write_text(json.dumps({'answer': str(count)}))
    print(count)

if __name__ == '__main__':
    main()
