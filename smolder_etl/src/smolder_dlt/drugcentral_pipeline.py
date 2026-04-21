"""
dlt pipeline: DrugCentral PostgreSQL → DuckDB

DrugCentral provides a public read-only PostgreSQL instance:
  Host:     unmtid-dbs.net
  Port:     5433
  Database: drugcentral
  User:     drugman
  Password: dosage

Tables loaded into DuckDB schema `drugcentral_raw`:
  structures      — drug structures with molecular properties
  approval        — regulatory approval records (FDA, EMA, etc.)
  act_table_full  — bioactivity / drug-target interactions
  drug_class      — pharmacological / therapeutic classifications
"""

import os
import dlt
from dlt.sources.sql_database import sql_database

DRUGCENTRAL_URL = (
    "postgresql+psycopg2://drugman:dosage@unmtid-dbs.net:5433/drugcentral"
)

DUCKDB_PATH = os.environ.get(
    "DUCKDB_PATH",
    "/app/data/prod.duckdb",
)

TABLES = ["structures", "approval", "act_table_full", "drug_class", "struct2drgclass"]


def build_source():
    return sql_database(
        credentials=DRUGCENTRAL_URL,
        schema="public",
        table_names=TABLES,
    )


def build_pipeline():
    return dlt.pipeline(
        pipeline_name="drugcentral",
        destination=dlt.destinations.duckdb(credentials=DUCKDB_PATH),
        dataset_name="drugcentral_raw",
    )


if __name__ == "__main__":
    pipeline = build_pipeline()
    load_info = pipeline.run(build_source())
    print(load_info)
