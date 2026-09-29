# cve

The four original data groups are provided as local Parquet tables.

Original group names remain below for interpreting the original optional hints. Paths are relative to this dataset root.

1. vulns_db
   - This database is provided as Parquet tables. It contains the structured NVD CVE registry: per-CVE publication metadata, CVSS v3 attack-vector information, and a sibling table holding the per-CVE CVSS score.
   - This database consists of two tables:
     - cves
       - Core CVE registry.
       - Fields:
         - cve_id (str): Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier
         - published (str): ISO timestamp when the CVE was published
         - last_modified (str): ISO timestamp of last NVD modification
         - vuln_status (str): NVD workflow status (e.g. "Analyzed", "Modified")
         - cvss3_attack_vector (str or null): NETWORK / ADJACENT_NETWORK / LOCAL / PHYSICAL
     - cvss_metadata
       - Per-CVE CVSS v3 base score.
       - Fields:
         - cve_id (str): Noisy CVE join key with the same recoverable structure as cves.cve_id
         - score_text (str): Exact CVSS v3 base score in a mixed text format; the CVSS score is the first numeric token in the field

2. cpe_db
   - This database is provided as Parquet tables. It contains the Common Platform Enumeration (CPE) match list — which products and versions are affected by each CVE — plus a vendor reference and version-details tables.
   - This database consists of three tables:
     - cpe_matches
       - One row per (CVE, affected product configuration) pair.
       - Fields:
         - cve_id (str): Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier
         - criteria (str): Product identifier string
         - vulnerable_flag (str): Indicates whether the configuration is vulnerable
     - vendor_aliases
       - Vendor reference table.
       - Fields:
         - alias (str)
         - canonical_vendor (str): Canonical lowercase vendor name (e.g. "apache", "microsoft")
     - cpe_version_details
       - Per-(CVE, criteria) version information.
       - Fields:
         - cve_id (str): Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier
         - criteria (str): The CPE criteria string this version detail belongs to
         - version_text (str or null): Affected version
         - version_start_inc (str or null): Inclusive lower bound of affected versions
         - version_start_exc (str or null): Exclusive lower bound of affected versions
         - version_end_inc (str or null): Inclusive upper bound of affected versions
         - version_end_exc (str or null): Exclusive upper bound of affected versions

3. kev_db
   - This database is provided as Parquet tables. It contains the CISA Known Exploited Vulnerabilities (KEV) catalog — CVEs that have been exploited in the wild.
   - This database consists of two tables:
     - kev_entries
       - One row per KEV-listed vulnerability.
       - Fields:
         - cve_ref (str): Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier
         - vendor_project (str): Vendor or project responsible for the affected product
         - products_csv (str): Affected product name(s)
         - vulnerability_name (str): Short human-readable name
         - date_added (str): Date the CVE was added to the KEV catalog
         - short_description (str): Brief description of the vulnerability
         - required_action (str): Action CISA requires affected agencies to take
         - due_date (str): Deadline by which required action must be completed
         - known_ransomware_use (str): "Known", "Unknown", or null
         - notes (str or null): Additional notes
     - kev_vendor_aliases
       - Agent-visible lookup from KEV vendor surface forms to canonical vendor names.
       - Fields:
         - vendor_project (str): Surface form appearing in kev_entries.vendor_project
         - canonical_vendor (str): Canonical lowercase vendor name

4. descriptions_db
   - This database is provided as Parquet tables. It contains free-text descriptions and external references for each CVE.
   - This database consists of one collection:
     - cve_documents
       - One document per CVE with embedded descriptions[] and references[].
       - Fields:
         - cve (str): Noisy CVE join key with source prefixes/suffixes/wrapper text, infix noise, and heterogeneous encodings of the original CVE identifier
         - descriptions (JSON array text): Free-text descriptions in one or more languages, each with:
           - lang (str): ISO language code (e.g. "en", "es")
           - value (str): Description prose
         - references (JSON array text): External reference URLs, each with:
           - url (str): Reference URL
           - source (str or null): Source organization that supplied the reference

## JSON representation

The original descriptions and references arrays are stored as reversible JSON array strings. Parse non-null strings with a JSON parser for nested access. Empty arrays remain `[]`; all element order, repeated references, object key order, URLs, language tags and text are preserved. The actual description key is `lang`, not `language` as stated in the original description. References have `url` and `source` keys; all present values are strings in this snapshot. The BSON documents contain only cve, descriptions and references: no `_id` is generated.

## Files and measured physical types

### cves

File: `data/vulns_db/cves.parquet`

| Column | Arrow type |
|---|---|
| `cve_id` | string |
| `published` | string |
| `last_modified` | string |
| `vuln_status` | string |
| `cvss3_attack_vector` | string |

### cvss_metadata

File: `data/vulns_db/cvss_metadata.parquet`

| Column | Arrow type |
|---|---|
| `cve_id` | string |
| `score_text` | string |

### cpe_matches

File: `data/cpe_db/cpe_matches.parquet`

| Column | Arrow type |
|---|---|
| `cve_id` | string |
| `criteria` | string |
| `vulnerable_flag` | string |

### cpe_version_details

File: `data/cpe_db/cpe_version_details.parquet`

| Column | Arrow type |
|---|---|
| `cve_id` | string |
| `criteria` | string |
| `version_text` | string |
| `version_start_inc` | string |
| `version_start_exc` | string |
| `version_end_inc` | string |
| `version_end_exc` | string |

### vendor_aliases

File: `data/cpe_db/vendor_aliases.parquet`

| Column | Arrow type |
|---|---|
| `alias` | string |
| `canonical_vendor` | string |

### kev_entries

File: `data/kev_db/kev_entries.parquet`

| Column | Arrow type |
|---|---|
| `cve_ref` | string |
| `vendor_project` | string |
| `products_csv` | string |
| `vulnerability_name` | string |
| `date_added` | string |
| `short_description` | string |
| `required_action` | string |
| `due_date` | string |
| `known_ransomware_use` | string |
| `notes` | string |

### kev_vendor_aliases

File: `data/kev_db/kev_vendor_aliases.parquet`

| Column | Arrow type |
|---|---|
| `vendor_project` | string |
| `canonical_vendor` | string |

### cve_documents

File: `data/descriptions_db/cve_documents.parquet`

| Column | Arrow type |
|---|---|
| `cve` | string |
| `descriptions` | string |
| `references` | string |

## Preservation

All source rows, duplicate/conflicting records, nulls, empty strings, noisy identifiers, flags, scores-as-text and version encodings remain unchanged. No identifier decoding, fuzzy matching, deduplication, severity classification, score extraction, truth-value inference, version normalization or answer computation is performed. PostgreSQL ordinary strings are interpreted with standard_conforming_strings=on; literal backslashes remain characters. The original kev_vendor_aliases.vendor_project PRIMARY KEY is recorded in metadata and checked for uniqueness/non-null values, but Parquet does not enforce database constraints.
