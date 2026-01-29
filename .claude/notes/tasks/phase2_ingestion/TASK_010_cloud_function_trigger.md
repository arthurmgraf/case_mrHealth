# TASK_010: Cloud Function Trigger (GCS Event)

## Description

Deploy a Cloud Function (2nd gen) that triggers automatically when new CSV files are uploaded to the GCS raw/csv_sales/ prefix. The function validates the file, processes it with pandas, and loads the result into BigQuery Bronze. This replaces the original architecture's Cloud Workflows + Dataproc combination.

## Prerequisites

- TASK_002 complete (Cloud Functions API enabled)
- TASK_003 complete (GCS bucket exists)
- TASK_004 complete (BigQuery datasets exist)
- TASK_009 complete (CSV files in GCS to test trigger)

## Steps

### Step 1: Create Cloud Function Source

Create `cloud_functions/csv_processor/main.py`:

```python
"""
Case Fictício - Teste -- CSV Processor Cloud Function
Triggered by GCS file upload events on raw/csv_sales/ prefix.
Processes pedido.csv and item_pedido.csv files into BigQuery Bronze layer.
"""

import functions_framework
import pandas as pd
import pyarrow
import io
import json
from datetime import datetime
from google.cloud import storage, bigquery


PROJECT = "case_ficticio-data-mvp"
BUCKET = "case_ficticio-data-lake-mvp"
BQ_DATASET = "case_ficticio_bronze"
QUARANTINE_PREFIX = "quarantine"

# Expected schemas
PEDIDO_COLUMNS = [
    "Id_Unidade", "Id_Pedido", "Tipo_Pedido", "Data_Pedido",
    "Vlr_Pedido", "Endereco_Entrega", "Taxa_Entrega", "Status"
]
ITEM_PEDIDO_COLUMNS = [
    "Id_Pedido", "Id_Item_Pedido", "Id_Produto", "Qtd", "Vlr_Item", "Observacao"
]

VALID_STATUSES = {"Finalizado", "Pendente", "Cancelado"}
VALID_ORDER_TYPES = {"Loja Online", "Loja Fisica"}


def read_csv_from_gcs(bucket_name: str, blob_name: str) -> pd.DataFrame:
    """Read a CSV file from GCS into a pandas DataFrame."""
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    content = blob.download_as_text(encoding="utf-8")
    return pd.read_csv(io.StringIO(content), sep=";")


def quarantine_file(bucket_name: str, source_blob: str, error_msg: str) -> None:
    """Move invalid file to quarantine with error report."""
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(bucket_name)

    # Copy file to quarantine
    source = bucket.blob(source_blob)
    quarantine_path = source_blob.replace("raw/csv_sales/", f"{QUARANTINE_PREFIX}/")
    bucket.copy_blob(source, bucket, quarantine_path)

    # Write error report
    error_report = {
        "source_file": source_blob,
        "error": error_msg,
        "timestamp": datetime.utcnow().isoformat(),
    }
    error_blob = bucket.blob(quarantine_path.replace(".csv", "_error.json"))
    error_blob.upload_from_string(json.dumps(error_report, indent=2))
    print(f"  [QUARANTINE] {source_blob}: {error_msg}")


def validate_pedido(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Validate pedido.csv data. Returns (valid_df, errors)."""
    errors = []

    # Check required columns
    missing = set(PEDIDO_COLUMNS) - set(df.columns)
    if missing:
        return pd.DataFrame(), [f"Missing columns: {missing}"]

    # Type casting
    df["Id_Unidade"] = pd.to_numeric(df["Id_Unidade"], errors="coerce")
    df["Vlr_Pedido"] = pd.to_numeric(df["Vlr_Pedido"], errors="coerce")
    df["Taxa_Entrega"] = pd.to_numeric(df["Taxa_Entrega"], errors="coerce")
    df["Data_Pedido"] = pd.to_datetime(df["Data_Pedido"], errors="coerce").dt.date

    # Remove nulls in required fields
    null_mask = df[["Id_Unidade", "Id_Pedido", "Data_Pedido", "Vlr_Pedido", "Status"]].isnull().any(axis=1)
    if null_mask.sum() > 0:
        errors.append(f"Dropped {null_mask.sum()} rows with null required fields")
    df = df[~null_mask]

    # Validate Status
    invalid_status = ~df["Status"].isin(VALID_STATUSES)
    if invalid_status.sum() > 0:
        errors.append(f"Dropped {invalid_status.sum()} rows with invalid Status")
    df = df[~invalid_status]

    # Deduplicate
    before = len(df)
    df = df.drop_duplicates(subset=["Id_Pedido"])
    if len(df) < before:
        errors.append(f"Removed {before - len(df)} duplicate orders")

    return df, errors


def validate_item_pedido(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Validate item_pedido.csv data. Returns (valid_df, errors)."""
    errors = []

    missing = set(ITEM_PEDIDO_COLUMNS) - set(df.columns)
    if missing:
        return pd.DataFrame(), [f"Missing columns: {missing}"]

    # Type casting
    df["Id_Produto"] = pd.to_numeric(df["Id_Produto"], errors="coerce")
    df["Qtd"] = pd.to_numeric(df["Qtd"], errors="coerce")
    df["Vlr_Item"] = pd.to_numeric(df["Vlr_Item"], errors="coerce")

    # Remove nulls in required fields
    null_mask = df[["Id_Pedido", "Id_Item_Pedido", "Id_Produto", "Qtd", "Vlr_Item"]].isnull().any(axis=1)
    if null_mask.sum() > 0:
        errors.append(f"Dropped {null_mask.sum()} rows with null required fields")
    df = df[~null_mask]

    # Deduplicate
    before = len(df)
    df = df.drop_duplicates(subset=["Id_Item_Pedido"])
    if len(df) < before:
        errors.append(f"Removed {before - len(df)} duplicate items")

    return df, errors


def load_to_bigquery(df: pd.DataFrame, table_name: str, source_file: str) -> int:
    """Load a DataFrame into BigQuery Bronze table."""
    client = bigquery.Client(project=PROJECT)
    table_id = f"{PROJECT}.{BQ_DATASET}.{table_name}"

    # Add metadata columns
    df["_source_file"] = source_file
    df["_ingest_timestamp"] = datetime.utcnow()
    df["_ingest_date"] = datetime.utcnow().date()

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    return len(df)


@functions_framework.cloud_event
def process_csv(cloud_event):
    """Main Cloud Function entry point -- triggered by GCS file upload."""
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    print(f"Processing: gs://{bucket_name}/{file_name}")

    # Only process CSV files in raw/csv_sales/
    if not file_name.startswith("raw/csv_sales/") or not file_name.endswith(".csv"):
        print(f"  [SKIP] Not a sales CSV: {file_name}")
        return

    # Determine file type
    base_name = file_name.split("/")[-1]

    try:
        df = read_csv_from_gcs(bucket_name, file_name)
        print(f"  Read {len(df)} rows from {base_name}")

        if base_name == "pedido.csv":
            df_valid, errors = validate_pedido(df)
            table = "orders"
        elif base_name == "item_pedido.csv":
            df_valid, errors = validate_item_pedido(df)
            table = "order_items"
        else:
            print(f"  [SKIP] Unknown file type: {base_name}")
            return

        if errors:
            for e in errors:
                print(f"  [WARN] {e}")

        if len(df_valid) == 0:
            quarantine_file(bucket_name, file_name, "No valid rows after validation")
            return

        rows_loaded = load_to_bigquery(df_valid, table, file_name)
        print(f"  [OK] Loaded {rows_loaded} rows into {BQ_DATASET}.{table}")

    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        print(f"  [ERROR] {error_msg}")
        quarantine_file(bucket_name, file_name, error_msg)
```

### Step 2: Create requirements.txt for Cloud Function

Create `cloud_functions/csv_processor/requirements.txt`:

```
functions-framework==3.*
google-cloud-storage==2.*
google-cloud-bigquery==3.*
pandas==2.*
pyarrow==14.*
db-dtypes==1.*
```

### Step 3: Deploy Cloud Function

```bash
cd cloud_functions/csv_processor

gcloud functions deploy csv-processor \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_csv \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=case_ficticio-data-lake-mvp" \
  --memory=256MB \
  --timeout=300s \
  --service-account=sa-case_ficticio-ingestion@case_ficticio-data-mvp.iam.gserviceaccount.com \
  --set-env-vars="PROJECT_ID=case_ficticio-data-mvp"
```

### Step 4: Test the Trigger

```bash
# Upload a single file to trigger the function
gsutil cp output/csv_sales/2026/01/28/unit_001/pedido.csv \
  gs://case_ficticio-data-lake-mvp/raw/csv_sales/2026/01/28/unit_001/pedido.csv

# Check function logs
gcloud functions logs read csv-processor --gen2 --region=us-central1 --limit=20

# Verify data in BigQuery
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as row_count FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders` WHERE _ingest_date = CURRENT_DATE()'
```

## Acceptance Criteria

- [ ] Cloud Function deploys successfully
- [ ] Function triggers on GCS file upload (pedido.csv)
- [ ] Function triggers on GCS file upload (item_pedido.csv)
- [ ] Valid data loads into BigQuery Bronze tables
- [ ] Invalid files are quarantined with error reports
- [ ] Function logs show processing details
- [ ] Function executes within 300s timeout

## Cost Impact

| Action | Cost |
|--------|------|
| Cloud Function deployment | Free (Cloud Build free tier) |
| Function invocations (~100/day) | Free (within 2M/month) |
| Compute (~2 sec/invocation, 256 MB) | Free (within 400K GB-sec/month) |
| **Total** | **$0.00** |

---

*TASK_010 of 26 -- Phase 2: Ingestion*
