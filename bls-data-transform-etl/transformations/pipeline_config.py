"""Shared configuration for the BLS Bronze -> Silver -> Gold declarative pipeline.

Declarative Pipeline transformation files (pipelines/bronze.py, silver.py, gold.py) run inside 
the pipeline's own Spark session. They read three keys from **pipeline configuration**
(Settings -> Configuration in the Pipeline UI

    catalog   (default: bls_pr)
    schema    (default: bls_time_series)
    volume    (default: bls_raw_files)

This module centralizes that lookup + the resulting source paths so every
transformation file references the same constants instead of re-deriving them.
"""

def resolve_volume_root(spark) -> str:
    """Reads catalog/schema/volume from pipeline configuration and builds the Volume root path."""
    catalog = spark.conf.get("catalog", "bls_pr")
    schema = spark.conf.get("schema", "bls_time_series")
    volume = spark.conf.get("volume","bls_raw_files")
    return f"/Volumes/{catalog}/{schema}/{volume}"

# Relative locations of the raw files within the Volume — preserved from the
# existing ingestion routine (bls_pipeline.py / run_ingestion), which
# syncs every file under "<volume_root>/<survey_code>/", including these
# small BLS lookup/mapping files alongside pr.data.1.AllData and pr.series.
BLS_DATA_RELATIVE_PATH = "pr/pr.data.1.AllData"
BLS_SERIES_RELATIVE_PATH = "pr/pr.series"
BLS_SECTOR_RELATIVE_PATH = "pr/pr.sector"
BLS_MEASURE_RELATIVE_PATH = "pr/pr.measure"
POPULATION_JSON_RELATIVE_PATH = "population/population_data.json"
