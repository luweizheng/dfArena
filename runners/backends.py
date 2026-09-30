"""Shared dataframe backend names and instructions for benchmark runners."""

BACKENDS = {
    "pandas": "Use pandas as the main dataframe backend for loading, transformation, and computation.",
    "polars": ("Use Polars as the main dataframe backend for loading, transformation, and computation. "
               "Do not use pandas for the main workflow. Pandas may be used only for an explicit final "
               "interoperability boundary when required."),
    "ibis": ("Use Ibis with DuckDB as the main dataframe backend for loading, filtering, joins, aggregation, "
             "sorting, and date handling. Keep relational computation lazy until final materialization where "
             "practical. Do not use pandas for the main workflow. A small final boundary conversion is allowed "
             "only when required for answer serialization."),
    "pyspark": ("Use the PySpark DataFrame API as the main backend for loading, transformation, and computation. "
                "Create a local SparkSession. Do not use pandas or the pandas API on Spark for the main workflow. "
                "Stop the SparkSession when finished."),
}
