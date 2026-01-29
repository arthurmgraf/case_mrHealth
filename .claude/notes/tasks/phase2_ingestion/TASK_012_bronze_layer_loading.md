# TASK_012: Bronze Layer Loading

## Description

Define the process for loading validated data into the Bronze layer. Data flows through two destinations: (1) GCS as Parquet files for archival and (2) BigQuery tables for querying. The Cloud Function (TASK_010) handles direct BigQuery loading. This task also covers an optional Parquet-to-GCS step for archival.

## Prerequisites

- TASK_010 complete (Cloud Function deployed)
- TASK_011 complete (Processing logic implemented)
- TASK_004 complete (BigQuery Bronze tables exist)

## Steps

### Step 1: BigQuery Direct Loading (Primary Path)

The Cloud Function loads data directly into BigQuery using `load_table_from_dataframe`. This is already implemented in TASK_010. The key configuration:

```python
from google.cloud import bigquery

def load_to_bronze_bq(df: pd.DataFrame, table_name: str) -> int:
    """Load validated DataFrame directly to BigQuery Bronze."""
    client = bigquery.Client(project=PROJECT)
    table_id = f"{PROJECT}.case_ficticio_bronze.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema_update_options=[
            bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
        ],
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    print(f"  [BQ] {table_name}: {table.num_rows} total rows")
    return len(df)
```

### Step 2: Parquet Archival to GCS (Optional Secondary Path)

For archival and to support future reprocessing:

```python
import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import storage
import io

def save_parquet_to_gcs(df: pd.DataFrame, table_name: str, ingest_date: str) -> str:
    """Save DataFrame as Parquet to GCS Bronze layer."""
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(BUCKET)

    # Convert to Parquet bytes
    table = pa.Table.from_pandas(df)
    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="snappy")
    buffer.seek(0)

    # Upload to GCS
    gcs_path = f"bronze/{table_name}/ingest_date={ingest_date}/{table_name}.snappy.parquet"
    blob = bucket.blob(gcs_path)
    blob.upload_from_file(buffer, content_type="application/octet-stream")

    print(f"  [GCS] Saved: gs://{BUCKET}/{gcs_path}")
    return f"gs://{BUCKET}/{gcs_path}"
```

### Step 3: Verify Bronze Loading

```sql
-- Check orders loaded today
SELECT
  _ingest_date,
  COUNT(*) as row_count,
  COUNT(DISTINCT id_pedido) as unique_orders,
  COUNT(DISTINCT id_unidade) as unique_units,
  MIN(data_pedido) as min_date,
  MAX(data_pedido) as max_date
FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`
WHERE _ingest_date = CURRENT_DATE()
GROUP BY _ingest_date;

-- Check order items loaded today
SELECT
  _ingest_date,
  COUNT(*) as row_count,
  COUNT(DISTINCT id_pedido) as unique_orders,
  COUNT(DISTINCT id_item_pedido) as unique_items
FROM `case_ficticio-data-mvp.case_ficticio_bronze.order_items`
WHERE _ingest_date = CURRENT_DATE()
GROUP BY _ingest_date;

-- Check for any duplicates
SELECT id_pedido, COUNT(*) as cnt
FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`
GROUP BY id_pedido
HAVING cnt > 1;
-- Expected: 0 rows (no duplicates)
```

### Step 4: Verify GCS Parquet Files

```bash
gsutil ls gs://case_ficticio-data-lake-mvp/bronze/orders/
gsutil ls gs://case_ficticio-data-lake-mvp/bronze/order_items/

# Check file size
gsutil du -s gs://case_ficticio-data-lake-mvp/bronze/
```

## Data Flow Summary

```
Cloud Function (TASK_010)
    |
    +---> [validate + clean] (TASK_011)
    |           |
    |     [valid data]       [invalid data]
    |           |                   |
    |     +-----+-----+      [quarantine/]
    |     |           |
    |     v           v
    | [BigQuery]  [GCS Parquet]
    | (primary)   (archival)
    |     |
    |     v
    | case_ficticio_bronze.orders
    | case_ficticio_bronze.order_items
```

## Acceptance Criteria

- [ ] Orders loaded into `case_ficticio_bronze.orders` with correct schema
- [ ] Order items loaded into `case_ficticio_bronze.order_items` with correct schema
- [ ] Metadata columns populated: _source_file, _ingest_timestamp, _ingest_date
- [ ] Partitioning by _ingest_date works correctly
- [ ] No duplicate records (verified by primary key check)
- [ ] Parquet files written to GCS (if archival path enabled)

## Cost Impact

| Action | Cost |
|--------|------|
| BigQuery load jobs | Free (load jobs do not count against query quota) |
| BigQuery storage (~50 MB) | Free (within 10 GB) |
| GCS Parquet storage (~30 MB) | Free (within 5 GB) |
| **Total** | **$0.00** |

---

*TASK_012 of 26 -- Phase 2: Ingestion*
