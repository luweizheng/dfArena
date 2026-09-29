# cve

The four original data groups are provided as local Parquet tables.

Original group names remain below for interpreting the original optional hints. Paths are relative to this dataset root.

## vulns_db

This database is provided as Parquet tables. It contains the structured NVD CVE registry: per-CVE publication metadata, CVSS v3 attack-vector information, and a sibling table holding the per-CVE CVSS score.

### cves

Core CVE registry.

File: `data/vulns_db/cves.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `cve_id` | string | Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier |
| `published` | string | ISO timestamp when the CVE was published |
| `last_modified` | string | ISO timestamp of last NVD modification |
| `vuln_status` | string | NVD workflow status (e.g. "Analyzed", "Modified") |
| `cvss3_attack_vector` | string | NETWORK / ADJACENT_NETWORK / LOCAL / PHYSICAL. May be null. |

### cvss_metadata

Per-CVE CVSS v3 base score.

File: `data/vulns_db/cvss_metadata.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `cve_id` | string | Noisy CVE join key with the same recoverable structure as cves.cve_id |
| `score_text` | string | Exact CVSS v3 base score in a mixed text format; the CVSS score is the first numeric token in the field |

## cpe_db

This database is provided as Parquet tables. It contains the Common Platform Enumeration (CPE) match list — which products and versions are affected by each CVE — plus a vendor reference and version-details tables.

### cpe_matches

One row per (CVE, affected product configuration) pair.

File: `data/cpe_db/cpe_matches.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `cve_id` | string | Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier |
| `criteria` | string | Product identifier string |
| `vulnerable_flag` | string | Indicates whether the configuration is vulnerable |

### vendor_aliases

Vendor reference table.

File: `data/cpe_db/vendor_aliases.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `alias` | string | — |
| `canonical_vendor` | string | Canonical lowercase vendor name (e.g. "apache", "microsoft") |

### cpe_version_details

Per-(CVE, criteria) version information.

File: `data/cpe_db/cpe_version_details.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `cve_id` | string | Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier |
| `criteria` | string | The CPE criteria string this version detail belongs to |
| `version_text` | string | Affected version. May be null. |
| `version_start_inc` | string | Inclusive lower bound of affected versions. May be null. |
| `version_start_exc` | string | Exclusive lower bound of affected versions. May be null. |
| `version_end_inc` | string | Inclusive upper bound of affected versions. May be null. |
| `version_end_exc` | string | Exclusive upper bound of affected versions. May be null. |

## kev_db

This database is provided as Parquet tables. It contains the CISA Known Exploited Vulnerabilities (KEV) catalog — CVEs that have been exploited in the wild.

### kev_entries

One row per KEV-listed vulnerability.

File: `data/kev_db/kev_entries.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `cve_ref` | string | Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier |
| `vendor_project` | string | Vendor or project responsible for the affected product |
| `products_csv` | string | Affected product name(s) |
| `vulnerability_name` | string | Short human-readable name |
| `date_added` | string | Date the CVE was added to the KEV catalog |
| `short_description` | string | Brief description of the vulnerability |
| `required_action` | string | Action CISA requires affected agencies to take |
| `due_date` | string | Deadline by which required action must be completed |
| `known_ransomware_use` | string | "Known", "Unknown", or null |
| `notes` | string | Additional notes. May be null. |

### kev_vendor_aliases

Agent-visible lookup from KEV vendor surface forms to canonical vendor names.

File: `data/kev_db/kev_vendor_aliases.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `vendor_project` | string | Surface form appearing in kev_entries.vendor_project |
| `canonical_vendor` | string | Canonical lowercase vendor name |

## descriptions_db

This database is provided as Parquet tables. It contains free-text descriptions and external references for each CVE.

### cve_documents

One document per CVE with embedded descriptions[] and references[].

File: `data/descriptions_db/cve_documents.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `cve` | string | Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier |
| `descriptions` | string | JSON array text. Free-text descriptions in one or more languages, each with: |
| `references` | string | JSON array text. External reference URLs, each with: |

Each `descriptions` element has:

- `lang` (string): ISO language code (e.g. "en", "es")
- `value` (string): Description prose

Each `references` element has:

- `url` (string): Reference URL
- `source` (string or null): Source organization that supplied the reference

## JSON representation

The original descriptions and references arrays are stored as reversible JSON array strings. Parse non-null strings with a JSON parser for nested access. Empty arrays remain `[]`; all element order, repeated references, object key order, URLs, language tags and text are preserved. The actual description key is `lang`, not `language` as stated in the original description. References have `url` and `source` keys; all present values are strings in this snapshot. The BSON documents contain only cve, descriptions and references: no `_id` is generated.

## Representation

kev_vendor_aliases.vendor_project is the source primary key. Parquet does not enforce database constraints.
