# krama

The three original data groups are provided as local Parquet tables. Original group names are retained below. All file paths are relative to this dataset root.

## domain_docs

Files from multiple domains, stored as plain text.

### files (domain_docs)

Every document has one field.

File: `data/domain_docs/files.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `content` | string | Full content as a plain string |

## geo_database

Geospatial and environmental data. Geometry columns use GeoPackage binary format.

### gacc_2025

Geographic boundaries and metadata of NIFC Geographic Area Coordination Centers (GACCs).

File: `data/geo/gacc_2025.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `OBJECTID` | int64 | Row identifier |
| `SHAPE` | binary | Polygon geometry of the GACC boundary (GeoPackage binary format) |
| `GeometryID` | string | Geometry identifier |
| `GACCUnitID` | string | Unit identifier |
| `ContactPhone` | string | Contact phone number |
| `Comments` | string | Additional notes |
| `DateCurrent` | string | Date last updated |
| `MapMethod` | string | Mapping methodology used |
| `GlobalID` | string | Global unique identifier |
| `GACCDescription` | string | Natural-language description of the GACC name, abbreviation, and location |

### usa_adm2

Geographic boundaries and metadata of US counties.

File: `data/geo/usa_adm2.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `fid` | int64 | Row identifier |
| `geom` | binary | Polygon geometry of the county (GeoPackage binary format) |
| `adm2_id` | string | County identifier |
| `adm2_src` | string | County source identifier |
| `adm2_name1` | string | Alternate county names |
| `adm2_name2` | string | Alternate county names |
| `adm1_id` | string | State identifier |
| `adm1_src` | string | State source identifier |
| `adm1_name1` | string | Alternate state names |
| `adm1_name2` | string | Alternate state names |
| `adm0_id` | string | Country identifier |
| `adm0_src` | string | Country source identifier |
| `adm0_name1` | string | Alternate country names |
| `adm0_name2` | string | Alternate country names |
| `src_lvl` | int64 | Source level |
| `src_lang` | string | Source language |
| `src_lang1` | string | Alternate source languages |
| `src_lang2` | string | Alternate source languages |
| `src_date` | string | Source date |
| `src_update` | string | Last update date |
| `src_name` | string | Source metadata |
| `src_lic` | string | Source metadata |
| `src_url` | string | Source metadata |
| `src_grp` | string | Source metadata |
| `adm_description` | string | Natural-language description of county, state, and country names |

### beach_water_temperature

Water and air temperature readings for Massachusetts beaches, with one row per measurement.

File: `data/geo/beach_water_temperature.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `community_code` | string | Community code |
| `county_code` | string | County code |
| `beach_name` | string | Beach name |
| `beach_type_description` | string | Beach type |
| `sample_date` | string | Sampling date |
| `water_temp` | string | Water temperature |
| `air_temp` | string | Air temperature |

## domain_assets

Binary files from multiple domains, stored as blobs.

### files (domain_assets)

Every row has two fields.

File: `data/domain_assets/files.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `file_description` | string | Natural-language description of file name and file type |
| `content` | binary | Full file content as a binary blob |

## Binary and document representation

The two tables called files belong to different groups: domain_docs/files contains content strings, whereas domain_assets/files contains file_description strings and content bytes. Use their distinct paths.

Document content contains full text, including embedded tables, document names, and newlines. No _id or separate domain/name columns are present. Binary content and geometry values are Parquet binary; geometry cells use the GeoPackage binary representation described above, not GeoParquet encoding.

SHAPE and geom contain bytes; DateCurrent, src_date and src_update contain strings despite their SQLite NUM declarations. All-null TEXT columns are nullable strings. Text-valued dates, temperatures, units, and identifiers remain strings.
