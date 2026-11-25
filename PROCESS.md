# PROCESS.md

## Architecture

### Medallion Data Layers

The pipeline uses a Medallion architecture to separate data ingestion, cleanup,
and business logic while maintaining clear lineage:

- **Bronze:** Stores raw source data with minimal transformation. Column names
  are sanitized, and nested population JSON is flattened into tabular records.
- **Silver:** Converts raw records into typed, reliable rows. Strings are
  trimmed, `year`, `value`, and `population` are cast to integers, and null
  values are removed.
- **Gold:** Applies business logic to validated Silver data: aggregation,
  joins, population statistics, best-year selection, and
  target-series-versus-population analysis.

The sources have different formats and ingestion requirements:

- BLS `/pr/` provides tab-delimited, fixed-format text discovered from an HTML
  directory listing.
- DataUSA provides nested JSON through a REST API.

The separate layers isolate parsing and schema issues while keeping every
processing stage testable and traceable.

### Modular Implementation

The implementation separates reusable Python components from the declarative
Databricks pipeline.

`bls_pipeline.py` contains scraping, HTTP HEAD checks, retry handling, and
idempotent synchronization. The driver notebook runs this ingestion step,
which safely lands the data before triggering the `bls-data-transform-etl`
declarative pipeline.

The Gold DataFrame implementation in `gold.py` is primary because it supports
isolated pytest coverage and clear, composable transformations. Spark SQL is
kept as a secondary implementation for the same analytical results.

## Trade-offs

The following enhancements would be appropriate for a production or
client-facing deployment:

- **Schema drift:** Validate Bronze schemas against versioned expectations,
  failing loudly or quarantining data instead of detecting drift in
  downstream layers.
- **Data volume:** Use Databricks Auto Loader for incremental discovery,
  checkpointing, and file-based ingestion. Also add pagination for large
  population API responses.
- **Access control:** Apply Unity Catalog grants and environment-specific
  RBAC to catalogs, schemas, and volumes.
- **API contracts:** Validate BLS and DataUSA requests and responses against
  versioned schemas or API specifications during ingestion.
- **Monitoring:** Replace print statements with structured logging and add
  audit tables or event-log metrics. Alert on pipeline, ingestion, or
  expectation-failure thresholds.
- **Scheduling:** Configure a Databricks job with a file-arrival trigger or
  cron schedule according to operational requirements.

## Retrospective

**Ingestion requirements**

The two sources required separate strategies. BLS `/pr/` data is flat-file
time-series content, while DataUSA is a REST API that returns nested population
records.

The initial BLS 403 was straightforward to resolve. Subsequent rate-limiting
required repeated debugging and was caused by bot-protection throttling frequent
requests. A polite delay and retry/backoff session resolved the issue.

**Best-year-per-series analysis**

The most difficult analytical requirement was interpreting "human-readable
label" for the coded `pr.series` format. AI assistance helped clarify the
intended labels.

The key was understanding how `series`, `sector`, and `measure` lookup files
connect to `pr.data.1.AllData`. The join requires mapping `series_id` to
`sector_code` and `measure_code`, then resolving the associated labels.
