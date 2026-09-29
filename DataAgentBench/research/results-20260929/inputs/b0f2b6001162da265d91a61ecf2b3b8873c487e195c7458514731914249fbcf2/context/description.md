# PATENTS

The two original data groups are available as local Parquet tables.  

Original group names are retained below for interpreting the original hints. File paths are relative to the dataset root.  

1. publication_database
   - This database is stored in Parquet format and contains natural-language metadata for published patents. Each record corresponds to a single patent publication, with descriptive fields for publication details, dates, classification codes, relationships, and citations.  
   - This database consists of one table:
    - publicationinfo:
      - Fields:  
        - Patents_info (str): Natural-language summary of the patent publication, including key identifiers and status like publication number, application number etc,.  
        - kind_code (str): Description of the publication kind code (e.g., type of document issued).  
        - application_kind (str): Type of application (e.g., “utility patent application”).  
        - pct_number (str): Patent Cooperation Treaty application number, if applicable.  
        - family_id (int64): Identifier linking related patents in the same family.  
        - title_localized (str): Patent title in localized language form.  
        - abstract_localized (str): Patent abstract in natural language.  
        - claims_localized_html (str): Claims section in HTML format containing readable text.  
        - description_localized_html (str): Description section in HTML format containing readable text.  
        - publication_date (str): Publication date in natural language format (e.g., “March 15th, 2020”).  
        - filing_date (str): Filing date in natural language format.  
        - grant_date (str): Grant date in in natural language format.  
        - priority_date (str): Priority date in in natural language format.  
        - priority_claim (str): List of claimed priority applications.  
        - inventor_harmonized (str): Harmonized list of inventors.  
        - examiner (str): Examiner(s) handling the case.  
        - uspc (str): United States Patent Classification code(s).  
        - ipc (str): International Patent Classification code(s).  
        - cpc (str): JSON-like list of Cooperative Patent Classification entries, each with code and metadata.  
        - citation (str): List of cited patents and non-patent literature.  
        - parent (str): Parent patent applications.  
        - child (str): Child patent applications.  
        - entity_status (str): Legal entity status of the assignee (e.g., “small entity”, “large entity”).  
        - art_unit (str): USPTO art unit assigned to the application.  

2. CPCDefinition_database
   - This database is stored in Parquet format and contains the hierarchical structure, definitions, and metadata for Cooperative Patent Classification (CPC) codes. Each record represents a CPC symbol at a specific hierarchy level, with parent-child relationships, references, and descriptive titles.  
   - This database consists of one table:
    - cpc_definition:
      - Fields (cpc_definition table):  
        - applicationReferences (str): Informative references to related applications.  
        - breakdownCode (bool): Indicates whether the symbol is a breakdown code.  
        - childGroups (str): JSON-like list of child CPC symbols at the next level.  
        - children (str): Additional JSON-like child references.  
        - dateRevised (double): Original numeric revision-date field; no date parsing or rescaling is performed.  
        - definition (str): Full definition of the CPC symbol.  
        - glossary (str): Glossary terms and explanations for the symbol.  
        - informativeReferences (str): Additional informative references.  
        - ipcConcordant (str): IPC concordance mapping for the CPC symbol.  
        - level (double): Hierarchical level of the CPC symbol (e.g., 1 to 5).  
        - limitingReferences (str): Scope-limiting references.  
        - notAllocatable (bool): Indicates whether this symbol can be assigned to a patent.  
        - parents (str): JSON-like list of parent CPC symbols in the hierarchy.  
        - precedenceLimitingReferences (str): Precedence-limiting references.  
        - residualReferences (str): Residual references for related but distinct subject matter.  
        - rules (str): Rules for interpreting and applying the CPC symbol.  
        - scopeLimitingReferences (str): Scope-limiting references for the symbol.  
        - status (str): Status of the CPC symbol (e.g., “active”, “deleted”).  
        - symbol (str): CPC classification code symbol.  
        - synonyms (str): Synonyms for the CPC symbol.  
        - titleFull (str): Full descriptive title of the CPC symbol.  
        - titlePart (str): Abbreviated or partial title of the CPC symbol.  

## Files and physical column types

### publicationinfo

File: `data/publication/publicationinfo.parquet`

| Column | Arrow type |
|---|---|
| `Patents_info` | string |
| `kind_code` | string |
| `application_kind` | string |
| `pct_number` | string |
| `family_id` | int64 |
| `title_localized` | string |
| `abstract_localized` | string |
| `claims_localized_html` | string |
| `description_localized_html` | string |
| `publication_date` | string |
| `filing_date` | string |
| `grant_date` | string |
| `priority_date` | string |
| `priority_claim` | string |
| `inventor_harmonized` | string |
| `examiner` | string |
| `uspc` | string |
| `ipc` | string |
| `cpc` | string |
| `citation` | string |
| `parent` | string |
| `child` | string |
| `entity_status` | string |
| `art_unit` | string |

### cpc_definition

File: `data/CPCDefinition/cpc_definition.parquet`

| Column | Arrow type |
|---|---|
| `applicationReferences` | string |
| `breakdownCode` | bool |
| `childGroups` | string |
| `children` | string |
| `dateRevised` | double |
| `definition` | string |
| `glossary` | string |
| `informativeReferences` | string |
| `ipcConcordant` | string |
| `level` | double |
| `limitingReferences` | string |
| `notAllocatable` | bool |
| `parents` | string |
| `precedenceLimitingReferences` | string |
| `residualReferences` | string |
| `rules` | string |
| `scopeLimitingReferences` | string |
| `status` | string |
| `symbol` | string |
| `synonyms` | string |
| `titleFull` | string |
| `titlePart` | string |

## Preservation

All original records, long HTML/text content, nulls, empty strings, and duplicate records are preserved without truncation or cleaning. Structured text stays text. Natural-language dates are not parsed. SQLite family_id retains integer storage; CPC level and dateRevised retain double storage; breakdownCode and notAllocatable retain boolean storage. No HTML, SQL text, citations, or other embedded content is executed during migration.

metadata.yaml enumerates the two configured input tables. A separate .part file in the original source directory is not referenced by db_config.yaml and is retained at the original location; it is not treated as an additional database table. Original hints are available in context/hints.md when enabled by the experiment.
