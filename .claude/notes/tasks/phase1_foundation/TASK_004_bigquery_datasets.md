# TASK_004: BigQuery Datasets Creation

## Description

Create BigQuery datasets for the Bronze, Silver, and Gold layers of the medallion architecture. BigQuery provides 10 GB of free active storage and 1 TB of free queries per month. Datasets are organized to reflect the architectural layers and enable granular access control.

## Prerequisites

- TASK_001 complete (GCP project exists)
- TASK_002 complete (BigQuery API enabled)

## Steps

### Step 1: Create Datasets

```bash
PROJECT="case_ficticio-data-mvp"
LOCATION="US"  # Must be US multi-region for free tier

# Bronze dataset -- raw data loaded from GCS (schema-enforced, deduplicated)
bq mk \
  --project_id=$PROJECT \
  --dataset \
  --location=$LOCATION \
  --description="Bronze layer: schema-enforced, deduplicated data from CSV and reference sources" \
  --label environment:mvp \
  --label layer:bronze \
  case_ficticio_bronze

# Silver dataset -- cleaned, enriched, normalized data
bq mk \
  --project_id=$PROJECT \
  --dataset \
  --location=$LOCATION \
  --description="Silver layer: cleaned, enriched, and normalized data with business rules applied" \
  --label environment:mvp \
  --label layer:silver \
  case_ficticio_silver

# Gold dataset -- business-ready dimensional model
bq mk \
  --project_id=$PROJECT \
  --dataset \
  --location=$LOCATION \
  --description="Gold layer: star schema dimensional model, KPIs, and aggregations" \
  --label environment:mvp \
  --label layer:gold \
  case_ficticio_gold

# Monitoring dataset -- pipeline metadata and quality logs
bq mk \
  --project_id=$PROJECT \
  --dataset \
  --location=$LOCATION \
  --description="Pipeline monitoring: ingestion logs, quality checks, processing metadata" \
  --label environment:mvp \
  --label layer:monitoring \
  case_ficticio_monitoring
```

### Step 2: Expected Table Structure

```
BigQuery Project: case_ficticio-data-mvp
|
+-- case_ficticio_bronze
|   +-- orders              (partitioned by ingest_date)
|   +-- order_items         (partitioned by ingest_date)
|   +-- products            (static reference table)
|   +-- units               (static reference table)
|   +-- states              (static reference table)
|   +-- countries           (static reference table)
|
+-- case_ficticio_silver
|   +-- orders              (partitioned by order_date, clustered by unit_id)
|   +-- order_items         (partitioned by ingest_date, clustered by order_id)
|   +-- products            (deduplicated, current records)
|   +-- units               (enriched with state/country)
|   +-- states              (normalized)
|   +-- countries           (normalized)
|
+-- case_ficticio_gold
|   +-- dim_date            (date dimension)
|   +-- dim_product         (product dimension)
|   +-- dim_unit            (unit dimension with geography)
|   +-- dim_geography       (state/country hierarchy)
|   +-- fact_sales          (order-level grain)
|   +-- fact_order_items    (item-level grain)
|   +-- agg_daily_sales     (daily KPI aggregation)
|   +-- agg_unit_performance (unit-level KPI aggregation)
|
+-- case_ficticio_monitoring
|   +-- pipeline_runs       (processing metadata)
|   +-- quality_checks      (data quality results)
```

### Step 3: Create Bronze Tables (DDL)

```sql
-- Execute in BigQuery Console or via bq command

-- Bronze: Orders
CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_bronze.orders` (
  id_unidade INT64 NOT NULL,
  id_pedido STRING NOT NULL,
  tipo_pedido STRING,
  data_pedido DATE,
  vlr_pedido NUMERIC(10,2),
  endereco_entrega STRING,
  taxa_entrega NUMERIC(10,2),
  status STRING,
  _source_file STRING,
  _ingest_timestamp TIMESTAMP,
  _ingest_date DATE
)
PARTITION BY _ingest_date
OPTIONS(
  description="Bronze layer: raw orders from unit CSV files",
  labels=[("layer", "bronze")]
);

-- Bronze: Order Items
CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_bronze.order_items` (
  id_pedido STRING NOT NULL,
  id_item_pedido STRING NOT NULL,
  id_produto INT64,
  qtd INT64,
  vlr_item NUMERIC(10,2),
  observacao STRING,
  _source_file STRING,
  _ingest_timestamp TIMESTAMP,
  _ingest_date DATE
)
PARTITION BY _ingest_date
OPTIONS(
  description="Bronze layer: raw order items from unit CSV files",
  labels=[("layer", "bronze")]
);

-- Bronze: Products (reference)
CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_bronze.products` (
  id_produto INT64 NOT NULL,
  nome_produto STRING,
  _ingest_timestamp TIMESTAMP
)
OPTIONS(
  description="Bronze layer: product reference data",
  labels=[("layer", "bronze"), ("source", "reference")]
);

-- Bronze: Units (reference)
CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_bronze.units` (
  id_unidade INT64 NOT NULL,
  nome_unidade STRING,
  id_estado INT64,
  _ingest_timestamp TIMESTAMP
)
OPTIONS(
  description="Bronze layer: unit reference data",
  labels=[("layer", "bronze"), ("source", "reference")]
);

-- Bronze: States (reference)
CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_bronze.states` (
  id_estado INT64 NOT NULL,
  id_pais INT64,
  nome_estado STRING,
  _ingest_timestamp TIMESTAMP
)
OPTIONS(
  description="Bronze layer: state reference data",
  labels=[("layer", "bronze"), ("source", "reference")]
);

-- Bronze: Countries (reference)
CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_bronze.countries` (
  id_pais INT64 NOT NULL,
  nome_pais STRING,
  _ingest_timestamp TIMESTAMP
)
OPTIONS(
  description="Bronze layer: country reference data",
  labels=[("layer", "bronze"), ("source", "reference")]
);
```

### Step 4: Run DDL via bq CLI

```bash
# Save the SQL above to a file, then execute:
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < bronze_tables.sql

# Or execute individual statements:
bq query --use_legacy_sql=false \
  'CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_bronze.orders` (
    id_unidade INT64 NOT NULL,
    id_pedido STRING NOT NULL,
    tipo_pedido STRING,
    data_pedido DATE,
    vlr_pedido NUMERIC(10,2),
    endereco_entrega STRING,
    taxa_entrega NUMERIC(10,2),
    status STRING,
    _source_file STRING,
    _ingest_timestamp TIMESTAMP,
    _ingest_date DATE
  )
  PARTITION BY _ingest_date'
```

### Step 5: Verify Datasets and Tables

```bash
# List all datasets
bq ls --project_id=case_ficticio-data-mvp

# List tables in bronze dataset
bq ls case_ficticio-data-mvp:case_ficticio_bronze

# Describe a table
bq show --schema case_ficticio-data-mvp:case_ficticio_bronze.orders
```

## Storage Budget Calculation

| Dataset | Tables | Estimated Rows/Month | Estimated Size |
|---------|--------|---------------------|----------------|
| case_ficticio_bronze | 6 | ~150K orders + items | ~50 MB |
| case_ficticio_silver | 6 | ~150K (transformed) | ~40 MB |
| case_ficticio_gold | 8 | ~150K + aggregations | ~30 MB |
| case_ficticio_monitoring | 2 | ~1K log entries | ~1 MB |
| **Total** | **22** | | **~120 MB (of 10 GB free)** |

## Acceptance Criteria

- [ ] 4 datasets created: case_ficticio_bronze, case_ficticio_silver, case_ficticio_gold, case_ficticio_monitoring
- [ ] All datasets in US multi-region location
- [ ] Bronze tables created with correct schemas
- [ ] Labels applied to all datasets
- [ ] Storage estimate confirms well within 10 GB free tier

## Cost Impact

| Action | Cost |
|--------|------|
| Dataset creation | Free |
| Table DDL execution | Free (0 bytes scanned) |
| Storage (< 10 GB active) | Free |
| **Total** | **$0.00** |

---

*TASK_004 of 26 -- Phase 1: Foundation*
