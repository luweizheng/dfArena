# DEPS_DEV_V1

Software package metadata, project metadata, and mappings between projects and package versions. All paths below are relative to the dataset root.

## Table: `packageinfo`

File: `data/package/packageinfo.parquet`

Metadata of software packages, including licenses, versions, dependency-processing status, and registry metadata.

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `System` | string | Package ecosystem, e.g. NPM or Maven. |
| `Name` | string | Package name, preserving its original spelling and separators. |
| `Version` | string | Package version string. |
| `Licenses` | string | License(s), stored as JSON-like array text. |
| `Links` | string | JSON-like list of links such as origin, documentation, or source code. |
| `Advisories` | string | JSON-like list of security advisories. |
| `VersionInfo` | string | JSON-like object with release metadata, e.g. `IsRelease` and `Ordinal`. |
| `Hashes` | string | JSON-like list of file hashes. |
| `DependenciesProcessed` | int64 | Whether dependencies have been processed, encoded as 0/1 integers. |
| `DependencyError` | int64 | Whether a dependency-processing error occurred, encoded as 0/1 integers. |
| `UpstreamPublishedAt` | double | Upstream publication timestamp as originally stored. The source description labels the unit as milliseconds, but the unit has not been verified; values are not rescaled or converted to dates. |
| `Registries` | string | JSON-like list of package registries. |
| `SLSAProvenance` | double | Described by the source as SLSA provenance level, if available. |
| `UpstreamIdentifiers` | string | JSON-like list of upstream identifiers. |
| `Purl` | double | Described by the source as package URL, if available. |

## Table: `project_packageversion`

File: `data/project/project_packageversion.parquet`

Mappings between projects and package versions.

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `System` | string | Package ecosystem, e.g. NPM. |
| `Name` | string | Package name. |
| `Version` | string | Package version string. |
| `ProjectType` | string | Project type, e.g. GITHUB. |
| `ProjectName` | string | Repository path in owner/repo format. |
| `RelationProvenance` | string | Provenance of the relationship data. |
| `RelationType` | string | Relationship type, e.g. source repository type. |

## Table: `project_info`

File: `data/project/project_info.parquet`

GitHub project information.

| Column | Parquet / Arrow type | Description |
|---|---|---|
| `Project_Information` | string | Textual information about the project, which may include its name, owner, and general purpose. |
| `Licenses` | string | Project licenses, stored as JSON-like array text. |
| `Description` | string | Project description, which may differ from Project_Information. |
| `Homepage` | string | Homepage URL, if available. |
| `OSSFuzz` | double | OSSFuzz status indicator, if applicable, as described by the source. |

## Representation

SLSAProvenance, Purl, and OSSFuzz are entirely null in this snapshot.

Additional relationship guidance is available in `context/hints.md` when enabled by the experiment configuration.
