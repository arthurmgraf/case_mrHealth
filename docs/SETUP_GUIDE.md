# MR. HEALTH Data Platform - Complete Setup Guide

**Replicate the entire platform from scratch in under 1 hour.**

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [GCP Project Setup](#2-gcp-project-setup)
3. [Enable Required APIs](#3-enable-required-apis)
4. [Create Cloud Storage Bucket](#4-create-cloud-storage-bucket)
5. [Create BigQuery Datasets & Tables](#5-create-bigquery-datasets--tables)
6. [Create Service Accounts & IAM](#6-create-service-accounts--iam)
7. [Install Python Dependencies](#7-install-python-dependencies)
8. [Generate & Upload Test Data](#8-generate--upload-test-data)
9. [Deploy Cloud Function](#9-deploy-cloud-function)
10. [Build Transformation Layers](#10-build-transformation-layers)
11. [Create Dashboards](#11-create-dashboards)
12. [Verify the Full Pipeline](#12-verify-the-full-pipeline)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Prerequisites

### Required Software

| Tool | Version | Install Link |
|------|---------|-------------|
| **Google Cloud SDK** (`gcloud`, `gsutil`, `bq`) | Latest | https://cloud.google.com/sdk/docs/install |
| **Python** | 3.11+ | https://www.python.org/downloads/ |
| **Git** | 2.x+ | https://git-scm.com/ |

### Required Accounts

- **Google Cloud Platform** account with a project and billing enabled (all services stay within the free tier)
- **Google Account** for Looker Studio access

### Verify Installation

```bash
gcloud --version        # Google Cloud SDK 400+
python --version        # Python 3.11+
git --version           # Git 2.x+
gsutil --version        # gsutil 5.x+
bq version              # BigQuery CLI
```

---

## 2. GCP Project Setup

### 2.1 Clone the Repository

```bash
git clone <repository-url>
cd mrhealth-data-platform
```

### 2.2 Create a GCP Project (if needed)

```bash
gcloud projects create YOUR_PROJECT_ID --name="MR Health Data Platform"
```

### 2.3 Set the Active Project

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a

# Verify the active project
gcloud config get-value project
```

### 2.4 Link a Billing Account

```bash
# List available billing accounts
gcloud billing accounts list

# Link billing to project (required even for free tier)
gcloud billing projects link YOUR_PROJECT_ID \
  --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### 2.5 Update Project Configuration

Edit `config/project_config.yaml` with your project details:

```yaml
project:
  id: YOUR_PROJECT_ID          # e.g., my-mrhealth-project
  name: MR Health Data Platform MVP
  region: us-central1
  environment: mvp

storage:
  bucket: YOUR_BUCKET_NAME     # e.g., mrhealth-datalake-XXXXX (must be globally unique)

bigquery:
  location: US
  datasets:
    bronze: case_ficticio_bronze
    silver: case_ficticio_silver
    gold: case_ficticio_gold
    monitoring: case_ficticio_monitoring
```

> **Note:** GCS bucket names must be globally unique. Append your project ID or a random suffix to ensure uniqueness.

---

## 3. Enable Required APIs

Enable all the GCP services used by the platform:

```bash
gcloud services enable \
  storage.googleapis.com \
  bigquery.googleapis.com \
  bigquerydatatransfer.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  eventarc.googleapis.com \
  run.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com
```

**PowerShell (Windows):**

```powershell
gcloud services enable `
  storage.googleapis.com `
  bigquery.googleapis.com `
  bigquerydatatransfer.googleapis.com `
  cloudfunctions.googleapis.com `
  cloudbuild.googleapis.com `
  cloudscheduler.googleapis.com `
  eventarc.googleapis.com `
  run.googleapis.com `
  monitoring.googleapis.com `
  logging.googleapis.com `
  iam.googleapis.com `
  cloudresourcemanager.googleapis.com
```

**Verify:**

```bash
gcloud services list --enabled --filter="name:(storage OR bigquery OR cloudfunctions OR eventarc OR run)"
```

---

## 4. Create Cloud Storage Bucket

### 4.1 Create the Bucket

```bash
gsutil mb \
  -p YOUR_PROJECT_ID \
  -c STANDARD \
  -l us-central1 \
  -b on \
  gs://YOUR_BUCKET_NAME/
```

**PowerShell:**

```powershell
gsutil mb `
  -p YOUR_PROJECT_ID `
  -c STANDARD `
  -l us-central1 `
  -b on `
  gs://YOUR_BUCKET_NAME/
```

### 4.2 Create the Prefix (Folder) Structure

The data lake follows this layout:

```
gs://YOUR_BUCKET_NAME/
  raw/
    csv_sales/          # Incoming sales CSVs (triggers Cloud Function)
    reference_data/     # Static reference tables
  bronze/               # Processed data staging
  quarantine/           # Invalid files with error reports
```

Create the structure:

```bash
# Bash / macOS / Linux
for prefix in \
  raw/csv_sales/.keep \
  raw/reference_data/.keep \
  bronze/orders/.keep \
  bronze/order_items/.keep \
  bronze/products/.keep \
  bronze/units/.keep \
  bronze/states/.keep \
  bronze/countries/.keep \
  quarantine/.keep; do
  echo "" | gsutil cp - gs://YOUR_BUCKET_NAME/$prefix
done
```

**PowerShell:**

```powershell
$prefixes = @(
    "raw/csv_sales/.keep",
    "raw/reference_data/.keep",
    "bronze/orders/.keep",
    "bronze/order_items/.keep",
    "bronze/products/.keep",
    "bronze/units/.keep",
    "bronze/states/.keep",
    "bronze/countries/.keep",
    "quarantine/.keep"
)

foreach ($prefix in $prefixes) {
    echo $null | gsutil cp - gs://YOUR_BUCKET_NAME/$prefix
}
```

### 4.3 Verify

```bash
gsutil ls gs://YOUR_BUCKET_NAME/
gsutil ls -r gs://YOUR_BUCKET_NAME/raw/
```

Expected output:

```
gs://YOUR_BUCKET_NAME/bronze/
gs://YOUR_BUCKET_NAME/quarantine/
gs://YOUR_BUCKET_NAME/raw/
```

---

## 5. Create BigQuery Datasets & Tables

### Option A: Using Python SDK (Recommended)

This is the preferred approach since it also creates the Bronze tables:

```bash
python scripts/deploy_phase1_infrastructure.py
```

This script creates:
- 4 BigQuery datasets: `case_ficticio_bronze`, `case_ficticio_silver`, `case_ficticio_gold`, `case_ficticio_monitoring`
- 6 Bronze layer tables: `orders`, `order_items`, `products`, `units`, `states`, `countries`

> **Alternative:** `scripts/setup_using_python_sdk.py` provides a standalone Python script that also creates the GCS bucket and prefix structure in addition to BigQuery resources. Use it if you prefer a single-script setup without requiring `gsutil` or `bq` CLI:
> ```bash
> python scripts/setup_using_python_sdk.py
> ```
> Note: Service account creation and API enablement still require `gcloud` CLI.

### Option B: Using `bq` CLI

```bash
# Create datasets
bq mk --project_id=YOUR_PROJECT_ID --dataset --location=US \
  --description="Bronze layer: schema-enforced, deduplicated data" \
  --label environment:mvp --label layer:bronze \
  case_ficticio_bronze

bq mk --project_id=YOUR_PROJECT_ID --dataset --location=US \
  --description="Silver layer: cleaned, enriched, normalized data" \
  --label environment:mvp --label layer:silver \
  case_ficticio_silver

bq mk --project_id=YOUR_PROJECT_ID --dataset --location=US \
  --description="Gold layer: star schema dimensional model and KPIs" \
  --label environment:mvp --label layer:gold \
  case_ficticio_gold

bq mk --project_id=YOUR_PROJECT_ID --dataset --location=US \
  --description="Pipeline monitoring: logs, quality checks, metadata" \
  --label environment:mvp --label layer:monitoring \
  case_ficticio_monitoring
```

**PowerShell:**

```powershell
bq mk --project_id=YOUR_PROJECT_ID --dataset --location=US `
  --description="Bronze layer: schema-enforced, deduplicated data" `
  --label environment:mvp --label layer:bronze `
  case_ficticio_bronze

bq mk --project_id=YOUR_PROJECT_ID --dataset --location=US `
  --description="Silver layer: cleaned, enriched, normalized data" `
  --label environment:mvp --label layer:silver `
  case_ficticio_silver

bq mk --project_id=YOUR_PROJECT_ID --dataset --location=US `
  --description="Gold layer: star schema dimensional model and KPIs" `
  --label environment:mvp --label layer:gold `
  case_ficticio_gold

bq mk --project_id=YOUR_PROJECT_ID --dataset --location=US `
  --description="Pipeline monitoring: logs, quality checks, metadata" `
  --label environment:mvp --label layer:monitoring `
  case_ficticio_monitoring
```

Then create the Bronze tables from the SQL file:

```bash
bq query --use_legacy_sql=false < sql/bronze/create_tables.sql
```

### Verify

```bash
# List datasets
bq ls --project_id=YOUR_PROJECT_ID

# Check a specific table schema
bq show --project_id=YOUR_PROJECT_ID case_ficticio_bronze.orders
```

---

## 6. Create Service Accounts & IAM

### 6.1 Create Service Accounts

```bash
# Ingestion pipeline service account
gcloud iam service-accounts create sa-mrhealth-ingestion \
  --project=YOUR_PROJECT_ID \
  --display-name="MR Health Ingestion Pipeline" \
  --description="Cloud Functions that process CSV files"

# Transformation layer service account
gcloud iam service-accounts create sa-mrhealth-transform \
  --project=YOUR_PROJECT_ID \
  --display-name="MR Health Transformation Layer" \
  --description="BigQuery scheduled queries and transformations"

# Monitoring service account
gcloud iam service-accounts create sa-mrhealth-monitoring \
  --project=YOUR_PROJECT_ID \
  --display-name="MR Health Monitoring" \
  --description="Pipeline monitoring and alerting"
```

### 6.2 Assign IAM Roles

```bash
SA_INGESTION="sa-mrhealth-ingestion@YOUR_PROJECT_ID.iam.gserviceaccount.com"
SA_TRANSFORM="sa-mrhealth-transform@YOUR_PROJECT_ID.iam.gserviceaccount.com"
SA_MONITORING="sa-mrhealth-monitoring@YOUR_PROJECT_ID.iam.gserviceaccount.com"

# Ingestion: read GCS + write BigQuery
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_INGESTION" --role="roles/storage.objectViewer" --quiet
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_INGESTION" --role="roles/storage.objectCreator" --quiet
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_INGESTION" --role="roles/bigquery.dataEditor" --quiet
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_INGESTION" --role="roles/bigquery.jobUser" --quiet

# Transformation: read/write BigQuery
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_TRANSFORM" --role="roles/bigquery.dataEditor" --quiet
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_TRANSFORM" --role="roles/bigquery.jobUser" --quiet

# Monitoring: read-only access
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_MONITORING" --role="roles/monitoring.viewer" --quiet
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_MONITORING" --role="roles/logging.viewer" --quiet
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_MONITORING" --role="roles/bigquery.metadataViewer" --quiet
```

### 6.3 Verify

```bash
gcloud iam service-accounts list --project=YOUR_PROJECT_ID
```

---

## 7. Install Python Dependencies

### 7.1 Create a Virtual Environment

```bash
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat
```

### 7.2 Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

| Package | Purpose |
|---------|---------|
| `faker` | Realistic test data generation |
| `pandas` | Data processing and transformation |
| `google-cloud-storage` | GCS bucket operations |
| `google-cloud-bigquery` | BigQuery table and query operations |
| `google-cloud-functions-framework` | Cloud Function local testing |
| `pyarrow` | Columnar data format (BigQuery load) |
| `pytest` | Unit testing framework |
| `pytest-cov` | Test coverage reporting |
| `ruff` | Python linter |

### 7.3 Authenticate with GCP

```bash
# Application Default Credentials (for local scripts)
gcloud auth application-default login

# Verify authentication
gcloud auth list
```

---

## 8. Generate & Upload Test Data

### 8.1 Generate Fake Sales Data

```bash
python scripts/generate_fake_sales.py
```

This generates realistic sales data under `output/`:
- **50 restaurant units** across southern Brazil (RS, SC, PR)
- **30 products** from a health/slow-food catalog
- **~5,000 orders/month** with line items
- Organized by date: `output/csv_sales/YYYY/MM/DD/unit_XXX/`

### 8.2 Upload Data to GCS

```bash
python scripts/upload_fake_data_to_gcs.py
```

This uploads:
- Reference data to `gs://YOUR_BUCKET_NAME/raw/reference_data/`
- Sales CSVs to `gs://YOUR_BUCKET_NAME/raw/csv_sales/`

### 8.3 Load Reference Data into BigQuery Bronze

```bash
python scripts/load_reference_data.py
```

Loads static reference tables (products, units, states, countries) into the Bronze layer.

### 8.4 Verify Upload

```bash
# Check GCS files
gsutil ls -r gs://YOUR_BUCKET_NAME/raw/reference_data/
gsutil ls gs://YOUR_BUCKET_NAME/raw/csv_sales/

# Check BigQuery reference tables
bq query --use_legacy_sql=false \
  "SELECT 'products' as tbl, COUNT(*) as rows FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.products\`
   UNION ALL
   SELECT 'units', COUNT(*) FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.units\`
   UNION ALL
   SELECT 'states', COUNT(*) FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.states\`
   UNION ALL
   SELECT 'countries', COUNT(*) FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.countries\`"
```

Expected output:

```
+-----------+------+
|    tbl    | rows |
+-----------+------+
| products  |   30 |
| units     |   50 |
| states    |    3 |
| countries |    1 |
+-----------+------+
```

---

## 9. Deploy Cloud Function

The Cloud Function triggers automatically when CSV files land in `raw/csv_sales/` and loads them into BigQuery Bronze.

### 9.1 Deploy

```bash
cd cloud_functions/csv_processor

gcloud functions deploy csv-processor \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_csv \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=YOUR_BUCKET_NAME" \
  --memory=256MB \
  --timeout=300s \
  --set-env-vars="PROJECT_ID=YOUR_PROJECT_ID,BUCKET_NAME=YOUR_BUCKET_NAME,BQ_DATASET=case_ficticio_bronze" \
  --allow-unauthenticated

cd ../..
```

**PowerShell:**

```powershell
cd cloud_functions\csv_processor

gcloud functions deploy csv-processor `
  --gen2 `
  --runtime=python311 `
  --region=us-central1 `
  --source=. `
  --entry-point=process_csv `
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" `
  --trigger-event-filters="bucket=YOUR_BUCKET_NAME" `
  --memory=256MB `
  --timeout=300s `
  --set-env-vars="PROJECT_ID=YOUR_PROJECT_ID,BUCKET_NAME=YOUR_BUCKET_NAME,BQ_DATASET=case_ficticio_bronze" `
  --allow-unauthenticated

cd ..\..
```

### 9.2 Test the Function

Upload a test file to trigger it:

```bash
gsutil cp output/csv_sales/2026/01/28/unit_001/pedido.csv \
  gs://YOUR_BUCKET_NAME/raw/csv_sales/test/pedido.csv
```

Check logs:

```bash
gcloud functions logs read csv-processor --gen2 --region=us-central1 --limit=20
```

Verify data landed in BigQuery:

```bash
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as row_count FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.orders\`"
```

### 9.3 Check Function Status

```bash
gcloud functions describe csv-processor --gen2 --region=us-central1
```

---

## 10. Build Transformation Layers

Once Bronze data is populated, build Silver and Gold layers:

### 10.1 Silver Layer (Cleaned & Enriched)

```bash
python scripts/build_silver_layer.py
```

Runs 3 SQL transformations:
1. `sql/silver/01_reference_tables.sql` - Clean reference data
2. `sql/silver/02_orders.sql` - Normalize orders, add date enrichment, deduplicate
3. `sql/silver/03_order_items.sql` - Transform line items, calculate totals

### 10.2 Gold Layer (Star Schema)

```bash
python scripts/build_gold_layer.py
```

Builds the dimensional model:
1. `sql/gold/01_dim_date.sql` - Date dimension (3-year date spine)
2. `sql/gold/02_dim_product.sql` - Product dimension
3. `sql/gold/03_dim_unit.sql` - Unit/restaurant dimension
4. `sql/gold/04_dim_geography.sql` - Geography hierarchy
5. `sql/gold/05_fact_sales.sql` - Order-level fact table (partitioned + clustered)
6. `sql/gold/06_fact_order_items.sql` - Line-level fact table

### 10.3 Aggregation Tables (Dashboard Performance)

```bash
python scripts/build_aggregations.py
```

Creates pre-aggregated tables:
1. `sql/gold/07_agg_daily_sales.sql` - Daily KPIs
2. `sql/gold/08_agg_unit_performance.sql` - Unit rankings
3. `sql/gold/09_agg_product_performance.sql` - Product metrics

### 10.4 Verify All Layers

```bash
python scripts/verify_infrastructure.py
```

Or manually:

```bash
bq query --use_legacy_sql=false "
SELECT 'bronze.orders' as layer_table, COUNT(*) as rows
  FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.orders\`
UNION ALL SELECT 'bronze.order_items', COUNT(*)
  FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.order_items\`
UNION ALL SELECT 'silver.orders', COUNT(*)
  FROM \`YOUR_PROJECT_ID.case_ficticio_silver.orders\`
UNION ALL SELECT 'silver.order_items', COUNT(*)
  FROM \`YOUR_PROJECT_ID.case_ficticio_silver.order_items\`
UNION ALL SELECT 'gold.fact_sales', COUNT(*)
  FROM \`YOUR_PROJECT_ID.case_ficticio_gold.fact_sales\`
UNION ALL SELECT 'gold.fact_order_items', COUNT(*)
  FROM \`YOUR_PROJECT_ID.case_ficticio_gold.fact_order_items\`
UNION ALL SELECT 'gold.agg_daily_sales', COUNT(*)
  FROM \`YOUR_PROJECT_ID.case_ficticio_gold.agg_daily_sales\`
ORDER BY layer_table
"
```

---

## 11. Create Dashboards

Follow the detailed Looker Studio guide: **[LOOKER_STUDIO_SETUP.md](LOOKER_STUDIO_SETUP.md)**

Quick summary:

1. Go to https://lookerstudio.google.com
2. Create 4 data sources pointing to Gold layer tables
3. Build 3 dashboards:
   - **Executive Overview** - Revenue trends, channel mix, growth
   - **Operations** - Unit rankings, product performance
   - **Pipeline Monitor** - Data freshness, ingestion volume

---

## 12. Verify the Full Pipeline

### Run Unit Tests

```bash
pytest tests/unit/ -v
```

Expected: 21/22 tests passing (97.2% coverage).

### Run with Coverage Report

```bash
pytest tests/unit/ -v --cov=scripts --cov-report=term-missing
```

### End-to-End Pipeline Test

```bash
# 1. Generate fresh data
python scripts/generate_fake_sales.py

# 2. Upload to GCS (triggers Cloud Function for Bronze ingestion)
python scripts/upload_fake_data_to_gcs.py

# 3. Load reference data
python scripts/load_reference_data.py

# 4. Wait for Cloud Function to finish (~3 minutes)
gcloud functions logs read csv-processor --gen2 --region=us-central1 --limit=50

# 5. Build Silver layer
python scripts/build_silver_layer.py

# 6. Build Gold layer
python scripts/build_gold_layer.py

# 7. Build aggregations
python scripts/build_aggregations.py

# 8. Verify all layers
python scripts/verify_infrastructure.py
```

### Check Monitoring Queries

```bash
# Data freshness
bq query --use_legacy_sql=false \
  "SELECT MAX(_ingest_date) AS last_ingest,
          DATE_DIFF(CURRENT_DATE(), MAX(_ingest_date), DAY) AS days_since
   FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.orders\`"

# Referential integrity
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) AS orphaned_items
   FROM \`YOUR_PROJECT_ID.case_ficticio_bronze.order_items\` oi
   LEFT JOIN \`YOUR_PROJECT_ID.case_ficticio_bronze.orders\` o ON oi.id_pedido = o.id_pedido
   WHERE o.id_pedido IS NULL"

# Free tier usage
bq query --use_legacy_sql=false \
  "SELECT DATE(creation_time) AS query_date,
          ROUND(SUM(total_bytes_processed) / 1e12, 4) AS tb_processed
   FROM \`YOUR_PROJECT_ID.region-us\`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
   WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
   GROUP BY query_date ORDER BY query_date DESC"
```

### Cloud Function Logs

```bash
# Recent executions
gcloud functions logs read csv-processor --gen2 --region=us-central1 --limit=50

# Errors only
gcloud functions logs read csv-processor --gen2 --region=us-central1 \
  --filter="severity=ERROR"

# Function details
gcloud functions describe csv-processor --gen2 --region=us-central1

# Event triggers
gcloud eventarc triggers list --location=us-central1
```

---

## 13. Troubleshooting

### Cloud Function Not Triggering

```bash
# Verify event trigger is configured
gcloud eventarc triggers list --location=us-central1

# Check function details and bucket binding
gcloud functions describe csv-processor --gen2 --region=us-central1

# Check bucket name matches exactly
gcloud functions describe csv-processor --gen2 --region=us-central1 | grep bucket

# Verify files are in the correct prefix
gsutil ls gs://YOUR_BUCKET_NAME/raw/csv_sales/
```

### Permission Errors

```bash
# Check current authenticated account
gcloud auth list

# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Verify project is set
gcloud config get-value project
```

### BigQuery Table Not Found

```bash
# List all datasets
bq ls --project_id=YOUR_PROJECT_ID

# List tables in a dataset
bq ls --project_id=YOUR_PROJECT_ID case_ficticio_bronze

# Re-create tables
python scripts/deploy_phase1_infrastructure.py
```

### Quarantined Files

```bash
# Check for quarantined files
gsutil ls gs://YOUR_BUCKET_NAME/quarantine/

# Read error report
gsutil cat gs://YOUR_BUCKET_NAME/quarantine/FILENAME_error_report.json
```

### Stale Dashboard Data

```powershell
# Rebuild all transformation layers
python scripts/build_silver_layer.py
python scripts/build_gold_layer.py
python scripts/build_aggregations.py

# Then refresh Looker Studio (Ctrl+R in browser)
```

---

## Quick Reference: All GCP Commands

### `gcloud` Commands

| Command | Purpose |
|---------|---------|
| `gcloud config set project ID` | Set active project |
| `gcloud config set compute/region REGION` | Set default region |
| `gcloud services enable SERVICE` | Enable a GCP API |
| `gcloud services list --enabled` | List enabled APIs |
| `gcloud iam service-accounts create NAME` | Create service account |
| `gcloud iam service-accounts list` | List service accounts |
| `gcloud projects add-iam-policy-binding` | Assign IAM roles |
| `gcloud functions deploy NAME` | Deploy Cloud Function |
| `gcloud functions describe NAME` | View function details |
| `gcloud functions logs read NAME` | View function logs |
| `gcloud eventarc triggers list` | List event triggers |
| `gcloud auth login` | Authenticate interactively |
| `gcloud auth application-default login` | Set application credentials |
| `gcloud billing accounts list` | List billing accounts |
| `gcloud billing projects link` | Link billing to project |

### `gsutil` Commands

| Command | Purpose |
|---------|---------|
| `gsutil mb gs://BUCKET/` | Create a new bucket |
| `gsutil cp FILE gs://BUCKET/PATH` | Upload file to GCS |
| `gsutil cp - gs://BUCKET/PATH` | Upload from stdin (create empty prefix) |
| `gsutil ls gs://BUCKET/` | List bucket contents |
| `gsutil ls -r gs://BUCKET/PREFIX/` | List recursively |
| `gsutil cat gs://BUCKET/FILE` | Read file contents |

### `bq` Commands

| Command | Purpose |
|---------|---------|
| `bq mk --dataset DATASET` | Create BigQuery dataset |
| `bq ls --project_id=ID` | List datasets in project |
| `bq show DATASET.TABLE` | Show table schema |
| `bq query "SQL"` | Run a SQL query |
| `bq query --use_legacy_sql=false "SQL"` | Run Standard SQL query |

### Python Scripts

| Script | Purpose |
|--------|---------|
| `scripts/deploy_phase1_infrastructure.py` | Create BQ datasets + Bronze tables |
| `scripts/setup_using_python_sdk.py` | Alternative: GCS + BQ setup via Python SDK |
| `scripts/generate_fake_sales.py` | Generate realistic test data |
| `scripts/upload_fake_data_to_gcs.py` | Upload data to GCS |
| `scripts/load_reference_data.py` | Load reference tables into Bronze |
| `scripts/verify_infrastructure.py` | Validate entire infrastructure |
| `scripts/build_silver_layer.py` | Run Silver layer SQL transformations |
| `scripts/build_gold_layer.py` | Build Gold star schema |
| `scripts/build_aggregations.py` | Create pre-aggregated KPI tables |

---

## Cost Summary

Every service used stays within the GCP Free Tier:

| Service | Free Tier Limit | This Project Uses |
|---------|----------------|-------------------|
| Cloud Storage | 5 GB | ~1 MB |
| BigQuery Storage | 10 GB | ~2 MB |
| BigQuery Queries | 1 TB/month | ~10 GB/month |
| Cloud Functions | 2M invocations/month | ~3K/month |
| Looker Studio | Unlimited | 3 dashboards |
| Eventarc | Free | 1 trigger |

**Monthly cost: $0.00**

---

**Document Version:** 1.0
**Last Updated:** 2026-01-29
