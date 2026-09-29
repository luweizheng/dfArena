# krama

The three original data groups are provided as local Parquet tables.

Here are the descriptions of these three data sources:

1. domain_docs
   - This database is provided as Parquet tables and contains files from multiple domains.
   - This database consists of one collection:
     - files
       - Every document has one field:
         - content (str): Full content as a plain string


2. geo_database
   - This database is provided as Parquet tables and contains geospatial and environmental data. Geometry columns store data in GeoPackage binary format.
   - This database consists of three tables:
     - gacc_2025
       - This table contains the geographic boundaries and metadata of NIFC Geographic Area Coordination Centers (GACCs).
       - Fields:
         - OBJECTID (int): Row identifier
         - SHAPE (blob): Polygon geometry of the GACC boundary (GeoPackage binary format)
         - GeometryID (text): Geometry identifier
         - GACCUnitID (text): Unit identifier
         - ContactPhone (text): Contact phone number
         - Comments (text): Additional notes
         - DateCurrent (text): Date last updated
         - MapMethod (text): Mapping methodology used
         - GlobalID (text): Global unique identifier
         - GACCDescription (text): Natural-language description of the GACC name, abbreviation, and location

     - usa_adm2
       - This table contains the geographic boundaries and metadata of US counties.
       - Fields:
         - fid (int): Row identifier
         - geom (blob): Polygon geometry of the county (GeoPackage binary format)
         - adm2_id (text): County identifier
         - adm2_src (text): County source identifier
         - adm2_name1, adm2_name2 (text): Alternate county names
         - adm1_id (text): State identifier
         - adm1_src (text): State source identifier
         - adm1_name1, adm1_name2 (text): Alternate state names
         - adm0_id (text): Country identifier
         - adm0_src (text): Country source identifier
         - adm0_name1, adm0_name2 (text): Alternate country names
         - src_lvl (int): Source level
         - src_lang (text): Source language
         - src_lang1, src_lang2 (text): Alternate source languages
         - src_date, src_update (text): Source date and last update date
         - src_name, src_lic, src_url, src_grp (text): Source metadata
         - adm_description (text): Natural-language description of county, state, and country names

     - beach_water_temperature
       - This table contains water and air temperature readings for Massachusetts beaches, with one row per measurement.
       - Fields:
         - community_code (text): Community code
         - county_code (text): County code
         - beach_name (text): Beach name
         - beach_type_description (text): Beach type
         - sample_date (text): Sampling date
         - water_temp (text): Water temperature
         - air_temp (text): Air temperature

3. domain_assets
   - This database is provided as Parquet tables and contains binary files from multiple domains stored as blobs.
   - This database consists of one table:
     - files
       - Every row has two fields:
         - file_description (text): Natural-language description of file name and file type
         - content (blob): Full file content as a binary blob

## Files and measured physical types

### domain_docs/files

File: `data/domain_docs/files.parquet`

| Column | Arrow type |
|---|---|
| `content` | string |

### geo/beach_water_temperature

File: `data/geo/beach_water_temperature.parquet`

| Column | Arrow type |
|---|---|
| `community_code` | string |
| `county_code` | string |
| `beach_name` | string |
| `beach_type_description` | string |
| `sample_date` | string |
| `water_temp` | string |
| `air_temp` | string |

### geo/gacc_2025

File: `data/geo/gacc_2025.parquet`

| Column | Arrow type |
|---|---|
| `OBJECTID` | int64 |
| `SHAPE` | binary |
| `GeometryID` | string |
| `GACCUnitID` | string |
| `ContactPhone` | string |
| `Comments` | string |
| `DateCurrent` | string |
| `MapMethod` | string |
| `GlobalID` | string |
| `GACCDescription` | string |

### geo/usa_adm2

File: `data/geo/usa_adm2.parquet`

| Column | Arrow type |
|---|---|
| `fid` | int64 |
| `geom` | binary |
| `adm2_id` | string |
| `adm2_src` | string |
| `adm2_name1` | string |
| `adm2_name2` | string |
| `adm1_id` | string |
| `adm1_src` | string |
| `adm1_name1` | string |
| `adm1_name2` | string |
| `adm0_id` | string |
| `adm0_src` | string |
| `adm0_name1` | string |
| `adm0_name2` | string |
| `src_lvl` | int64 |
| `src_lang` | string |
| `src_lang1` | string |
| `src_lang2` | string |
| `src_date` | string |
| `src_update` | string |
| `src_name` | string |
| `src_lic` | string |
| `src_url` | string |
| `src_grp` | string |
| `adm_description` | string |

### domain_assets/files

File: `data/domain_assets/files.parquet`

| Column | Arrow type |
|---|---|
| `file_description` | string |
| `content` | binary |

## Binary and document representation

The two tables called files belong to different groups: domain_docs/files contains content strings, whereas domain_assets/files contains file_description strings and content bytes. Use their distinct paths.

Document content is the full original string, including embedded tables, prose, document names and newlines. No _id or inferred domain/name columns are added. Binary content and geometry values are preserved byte-for-byte as Parquet binary, without base64, extraction, decompression, geometry transformation or file execution. Geometry bytes retain the source GeoPackage binary representation described above; this is ordinary Parquet containing raw geometry bytes, not a newly converted GeoParquet geometry column.

SQLite declarations such as NUM do not determine the type of every stored value. SHAPE and geom actually contain bytes; DateCurrent, src_date and src_update actually contain strings. These observed types are retained, with original declarations and storage counts recorded in metadata.yaml. All-null source TEXT columns remain nullable strings. Numeric-looking dates, temperatures, units and identifiers are not parsed or normalized. All rows, repeated records, nulls, empty values, whitespace and binary zero bytes are retained.
