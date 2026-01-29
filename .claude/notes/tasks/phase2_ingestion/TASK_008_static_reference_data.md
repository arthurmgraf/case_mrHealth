# TASK_008: Static Reference Data Export

## Description

Load static reference data (products, units, states, countries) into BigQuery Bronze layer. For the MVP, these tables are treated as static exports rather than using Datastream CDC. The fake data generator (TASK_005) already produces these CSVs. This task creates a script to upload them to GCS and load into BigQuery.

## Prerequisites

- TASK_003 complete (GCS bucket exists)
- TASK_004 complete (BigQuery datasets exist)
- TASK_005 complete (reference CSVs generated in output/reference_data/)

## Steps

### Step 1: Create Reference Data Loader Script

Create `scripts/load_reference_data.py`:

```python
#!/usr/bin/env python3
"""
Load static reference data CSVs into GCS and BigQuery Bronze layer.

Usage:
    python load_reference_data.py --source-dir ./output/reference_data
    python load_reference_data.py --source-dir ./output/reference_data --project case_ficticio-data-mvp
"""

import argparse
from pathlib import Path
from google.cloud import storage, bigquery


PROJECT = "case_ficticio-data-mvp"
BUCKET = "case_ficticio-data-lake-mvp"
DATASET = "case_ficticio_bronze"
GCS_PREFIX = "raw/reference_data"

# Mapping: CSV filename -> BigQuery table name and schema
TABLE_CONFIG = {
    "produto.csv": {
        "table": "products",
        "schema": [
            bigquery.SchemaField("id_produto", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("nome_produto", "STRING"),
            bigquery.SchemaField("_ingest_timestamp", "TIMESTAMP"),
        ],
    },
    "unidade.csv": {
        "table": "units",
        "schema": [
            bigquery.SchemaField("id_unidade", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("nome_unidade", "STRING"),
            bigquery.SchemaField("id_estado", "INT64"),
            bigquery.SchemaField("_ingest_timestamp", "TIMESTAMP"),
        ],
    },
    "estado.csv": {
        "table": "states",
        "schema": [
            bigquery.SchemaField("id_estado", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("id_pais", "INT64"),
            bigquery.SchemaField("nome_estado", "STRING"),
            bigquery.SchemaField("_ingest_timestamp", "TIMESTAMP"),
        ],
    },
    "pais.csv": {
        "table": "countries",
        "schema": [
            bigquery.SchemaField("id_pais", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("nome_pais", "STRING"),
            bigquery.SchemaField("_ingest_timestamp", "TIMESTAMP"),
        ],
    },
}


def upload_to_gcs(source_dir: Path, bucket_name: str, prefix: str) -> list[str]:
    """Upload all reference CSVs to GCS."""
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(bucket_name)
    uploaded = []

    for csv_file in source_dir.glob("*.csv"):
        blob_name = f"{prefix}/{csv_file.name}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(csv_file))
        uploaded.append(f"gs://{bucket_name}/{blob_name}")
        print(f"  [OK] Uploaded: {csv_file.name} -> gs://{bucket_name}/{blob_name}")

    return uploaded


def load_to_bigquery(bucket_name: str, prefix: str, dataset: str) -> None:
    """Load reference CSVs from GCS into BigQuery Bronze tables."""
    client = bigquery.Client(project=PROJECT)

    for csv_name, config in TABLE_CONFIG.items():
        table_id = f"{PROJECT}.{dataset}.{config['table']}"
        uri = f"gs://{bucket_name}/{prefix}/{csv_name}"

        job_config = bigquery.LoadJobConfig(
            schema=config["schema"][:-1],  # Exclude _ingest_timestamp (auto-added)
            skip_leading_rows=1,
            source_format=bigquery.SourceFormat.CSV,
            field_delimiter=";",
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()  # Wait for completion

        table = client.get_table(table_id)
        print(f"  [OK] Loaded {table.num_rows} rows into {table_id}")


def main():
    parser = argparse.ArgumentParser(description="Load reference data to GCS and BigQuery")
    parser.add_argument("--source-dir", type=str, default="./output/reference_data")
    parser.add_argument("--project", type=str, default=PROJECT)
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        print("Run generate_fake_sales.py first to create reference data.")
        return

    print("Step 1: Uploading reference CSVs to GCS...")
    upload_to_gcs(source_dir, BUCKET, GCS_PREFIX)

    print("\nStep 2: Loading into BigQuery Bronze...")
    load_to_bigquery(BUCKET, GCS_PREFIX, DATASET)

    print("\nDone! Reference data loaded into BigQuery Bronze layer.")


if __name__ == "__main__":
    main()
```

### Step 2: Run the Script

```bash
# Ensure reference data exists
ls output/reference_data/
# Expected: estado.csv  pais.csv  produto.csv  unidade.csv

# Upload and load
python scripts/load_reference_data.py --source-dir ./output/reference_data
```

### Step 3: Verify in BigQuery

```sql
-- Check row counts
SELECT 'products' as tbl, COUNT(*) as rows FROM `case_ficticio-data-mvp.case_ficticio_bronze.products`
UNION ALL
SELECT 'units', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_bronze.units`
UNION ALL
SELECT 'states', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_bronze.states`
UNION ALL
SELECT 'countries', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_bronze.countries`;

-- Expected:
-- products: 30
-- units: 50
-- states: 3
-- countries: 1
```

### Step 4: Verify in GCS

```bash
gsutil ls gs://case_ficticio-data-lake-mvp/raw/reference_data/
# Expected: 4 CSV files
```

## Future Refresh Procedure (Out of MVP Scope)

When reference data needs updating in production:

1. Export updated CSVs from PostgreSQL: `psql -c "COPY produto TO STDOUT CSV HEADER DELIMITER ';'" > produto.csv`
2. Re-run: `python scripts/load_reference_data.py --source-dir ./updated_data/`
3. BigQuery tables are truncated and reloaded (WRITE_TRUNCATE)
4. Future: implement Cloud Scheduler job to automate weekly refresh

## Acceptance Criteria

- [ ] All 4 reference CSVs uploaded to GCS raw/reference_data/
- [ ] All 4 BigQuery Bronze tables populated with correct row counts
- [ ] Data types match expected schema
- [ ] Script is idempotent (safe to re-run)

## Cost Impact

| Action | Cost |
|--------|------|
| GCS upload (~10 KB) | Free |
| BigQuery load jobs (4 jobs) | Free (0 bytes scanned for loads) |
| BigQuery storage (~1 KB) | Free |
| **Total** | **$0.00** |

---

*TASK_008 of 26 -- Phase 2: Ingestion*
