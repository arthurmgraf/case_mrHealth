# MR. HEALTH Data Platform - Data Architecture

**Complete Data Structure Reference**

---

## 📋 Table of Contents

- [GCS Bucket Structure](#gcs-bucket-structure)
- [CSV File Schemas](#csv-file-schemas)
- [BigQuery Datasets](#bigquery-datasets)
  - [Bronze Layer](#bronze-layer-raw--schema-enforced)
  - [Silver Layer](#silver-layer-cleaned--enriched)
  - [Gold Layer](#gold-layer-star-schema--aggregations)
- [Data Flow](#data-flow)
- [Scripts & Execution Order](#scripts--execution-order)
- [SQL Transformations](#sql-transformations)

---

## 🗂️ GCS Bucket Structure

**Bucket Name:** `gs://mrhealth-datalake-485810/`

### Folder Hierarchy

```
gs://mrhealth-datalake-485810/
│
├── raw/
│   ├── csv_sales/                  # Daily sales data from units
│   │   └── {YYYY}/
│   │       └── {MM}/
│   │           └── {DD}/
│   │               └── unit_{NNN}/
│   │                   ├── pedido.csv         # Orders (one file per unit per day)
│   │                   └── item_pedido.csv    # Order items (one file per unit per day)
│   │
│   └── reference/                  # Static reference data
│       ├── produto.csv             # Product catalog (30 products)
│       ├── unidade.csv             # Unit/restaurant list (50 units)
│       ├── estado.csv              # States (3: RS, SC, PR)
│       └── pais.csv                # Countries (1: Brasil)
│
└── quarantine/                     # Invalid/rejected files (if any)
    └── {timestamp}_{original_filename}
```

### File Naming Conventions

| File Type | Pattern | Example | Frequency |
|-----------|---------|---------|-----------|
| **Orders** | `pedido.csv` | `2026/01/28/unit_001/pedido.csv` | Daily per unit |
| **Order Items** | `item_pedido.csv` | `2026/01/28/unit_001/item_pedido.csv` | Daily per unit |
| **Products** | `produto.csv` | `reference/produto.csv` | One-time load |
| **Units** | `unidade.csv` | `reference/unidade.csv` | One-time load |

### Data Volume Estimates

| Data Type | Daily Volume | Monthly Volume | Annual Volume |
|-----------|--------------|----------------|---------------|
| **Orders** | 50 files × 3 KB = 150 KB | ~4.5 MB | ~55 MB |
| **Order Items** | 50 files × 10 KB = 500 KB | ~15 MB | ~180 MB |
| **Total Sales Data** | ~650 KB/day | ~20 MB/month | ~240 MB/year |
| **Reference Data** | Static (1 KB) | Static | Static |

**Note:** Current test data covers 2 days (2026-01-27, 2026-01-28) for 3 units.

---

## 📄 CSV File Schemas

### 1. pedido.csv (Orders)

**Separator:** Semicolon (`;`)
**Encoding:** UTF-8
**Header Row:** Yes

| Column | Data Type | Description | Example | Nullable |
|--------|-----------|-------------|---------|----------|
| `Id_Unidade` | INTEGER | Unit/restaurant ID | `1` | No |
| `Id_Pedido` | UUID | Unique order identifier | `55abc6e7-a05f-4c5c-aa7d-8d2641da9b4a` | No |
| `Tipo_Pedido` | STRING | Order type | `"Loja Online"` or `"Loja Fisica"` | No |
| `Data_Pedido` | DATE | Order date | `2026-01-28` | No |
| `Vlr_Pedido` | NUMERIC(10,2) | Total order value (BRL) | `187.99` | No |
| `Endereco_Entrega` | STRING | Delivery address | `"Rua Example, 123"` | Yes (null for physical) |
| `Taxa_Entrega` | NUMERIC(10,2) | Delivery fee (BRL) | `11.99` or `0.00` | No |
| `Status` | STRING | Order status | `"Finalizado"`, `"Cancelado"`, `"Pendente"` | No |

**Sample Row:**
```csv
Id_Unidade;Id_Pedido;Tipo_Pedido;Data_Pedido;Vlr_Pedido;Endereco_Entrega;Taxa_Entrega;Status
1;55abc6e7-a05f-4c5c-aa7d-8d2641da9b4a;Loja Online;2026-01-28;187.99;Colônia Natália Vargas;11.99;Finalizado
```

**Business Rules:**
- Physical store orders (`Loja Fisica`) MUST have `Taxa_Entrega = 0.00`
- Physical store orders MUST have `Endereco_Entrega` empty/null
- Online orders (`Loja Online`) typically have delivery fees > 0

### 2. item_pedido.csv (Order Items)

**Separator:** Semicolon (`;`)
**Encoding:** UTF-8
**Header Row:** Yes

| Column | Data Type | Description | Example | Nullable |
|--------|-----------|-------------|---------|----------|
| `Id_Pedido` | UUID | Order ID (foreign key to pedido) | `55abc6e7-a05f-4c5c-aa7d-8d2641da9b4a` | No |
| `Id_Item_Pedido` | UUID | Unique item identifier | `9172d8b4-89b1-4b87-8ac7-ebf21da5926f` | No |
| `Id_Produto` | INTEGER | Product ID (foreign key) | `8` | No |
| `Qtd` | INTEGER | Quantity purchased | `2` | No |
| `Vlr_Item` | NUMERIC(10,2) | Item unit price (BRL) | `19.90` | No |
| `Observacao` | STRING | Customer notes/observations | `"Sem cebola"` | Yes |

**Sample Row:**
```csv
Id_Pedido;Id_Item_Pedido;Id_Produto;Qtd;Vlr_Item;Observacao
55abc6e7-a05f-4c5c-aa7d-8d2641da9b4a;9172d8b4-89b1-4b87-8ac7-ebf21da5926f;8;2;19.90;
```

**Referential Integrity:**
- Every `Id_Pedido` MUST exist in `pedido.csv`
- Every `Id_Produto` MUST exist in `produto.csv`
- `Vlr_Item * Qtd` contributes to `Vlr_Pedido` (excluding delivery fee)

### 3. produto.csv (Products - Reference)

**Separator:** Semicolon (`;`)
**Encoding:** UTF-8
**Header Row:** Yes

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `Id_Produto` | INTEGER | Primary key | `1` |
| `Nome_Produto` | STRING | Product name | `"Bowl de Acai Premium"` |

**Sample Data:** 30 health/slow-food products (Açaí bowls, salads, wraps, juices, etc.)

### 4. unidade.csv (Units - Reference)

**Separator:** Semicolon (`;`)
**Encoding:** UTF-8
**Header Row:** Yes

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `Id_Unidade` | INTEGER | Primary key | `1` |
| `Nome_Unidade` | STRING | Restaurant name | `"MR. HEALTH - Porto Alegre Centro"` |
| `Id_Estado` | INTEGER | State ID (foreign key) | `1` |

**Sample Data:** 50 units across southern Brazil (RS, SC, PR)

### 5. estado.csv (States - Reference)

**Separator:** Semicolon (`;`)
**Encoding:** UTF-8
**Header Row:** Yes

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `Id_Estado` | INTEGER | Primary key | `1` |
| `Id_Pais` | INTEGER | Country ID (foreign key) | `1` |
| `Nome_Estado` | STRING | State name | `"Rio Grande do Sul"` |

**Sample Data:** 3 southern Brazil states

### 6. pais.csv (Countries - Reference)

**Separator:** Semicolon (`;`)
**Encoding:** UTF-8
**Header Row:** Yes

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `Id_Pais` | INTEGER | Primary key | `1` |
| `Nome_Pais` | STRING | Country name | `"Brasil"` |

**Sample Data:** 1 country (Brasil)

---

## 🏗️ BigQuery Datasets

**Project ID:** `sixth-foundry-485810-e5`

### Bronze Layer (Raw + Schema Enforced)

**Dataset:** `mrhealth_bronze`
**Purpose:** Preserve raw data exactly as received with schema enforcement and metadata tracking

#### Tables

##### 1. `orders`

| Column | Type | Description | Partitioned | Clustered |
|--------|------|-------------|-------------|-----------|
| `id_unidade` | INT64 | Unit ID | No | No |
| `id_pedido` | STRING | Order ID (UUID) | No | No |
| `tipo_pedido` | STRING | Order type | No | No |
| `data_pedido` | DATE | Order date | No | No |
| `vlr_pedido` | NUMERIC(10,2) | Order value | No | No |
| `endereco_entrega` | STRING | Delivery address | No | No |
| `taxa_entrega` | NUMERIC(10,2) | Delivery fee | No | No |
| `status` | STRING | Order status | No | No |
| `_source_file` | STRING | Source CSV path | No | No |
| `_ingest_timestamp` | TIMESTAMP | Ingestion time | No | No |
| `_ingest_date` | DATE | Ingestion date | **Yes** | No |

**Partitioning:** By `_ingest_date` (daily partitions for cost optimization)

##### 2. `order_items`

| Column | Type | Description | Partitioned | Clustered |
|--------|------|-------------|-------------|-----------|
| `id_pedido` | STRING | Order ID (FK) | No | No |
| `id_item_pedido` | STRING | Item ID (UUID) | No | No |
| `id_produto` | INT64 | Product ID (FK) | No | No |
| `qtd` | INT64 | Quantity | No | No |
| `vlr_item` | NUMERIC(10,2) | Item price | No | No |
| `observacao` | STRING | Customer notes | No | No |
| `_source_file` | STRING | Source CSV path | No | No |
| `_ingest_timestamp` | TIMESTAMP | Ingestion time | No | No |
| `_ingest_date` | DATE | Ingestion date | **Yes** | No |

**Partitioning:** By `_ingest_date`

##### 3. `products` (Reference)

| Column | Type | Description |
|--------|------|-------------|
| `id_produto` | INT64 | Primary key |
| `nome_produto` | STRING | Product name |
| `_ingest_timestamp` | TIMESTAMP | Load timestamp |

**Rows:** 30 products

##### 4. `units` (Reference)

| Column | Type | Description |
|--------|------|-------------|
| `id_unidade` | INT64 | Primary key |
| `nome_unidade` | STRING | Unit name |
| `id_estado` | INT64 | State ID (FK) |
| `_ingest_timestamp` | TIMESTAMP | Load timestamp |

**Rows:** 50 units

##### 5. `states` (Reference)

| Column | Type | Description |
|--------|------|-------------|
| `id_estado` | INT64 | Primary key |
| `id_pais` | INT64 | Country ID (FK) |
| `nome_estado` | STRING | State name |
| `_ingest_timestamp` | TIMESTAMP | Load timestamp |

**Rows:** 3 states

##### 6. `countries` (Reference)

| Column | Type | Description |
|--------|------|-------------|
| `id_pais` | INT64 | Primary key |
| `nome_pais` | STRING | Country name |
| `_ingest_timestamp` | TIMESTAMP | Load timestamp |

**Rows:** 1 country

---

### Silver Layer (Cleaned + Enriched)

**Dataset:** `mrhealth_silver`
**Purpose:** Clean, normalize, and enrich data for analytics consumption

#### Transformations Applied

1. **Null Handling:** COALESCE for optional fields
2. **Data Type Conversions:** Ensure proper NUMERIC types
3. **Business Rule Application:**
   - Physical orders forced to `taxa_entrega = 0.00`
   - Physical orders forced to `endereco_entrega = NULL`
4. **Reference Data Enrichment:** Join units with states and countries
5. **Data Quality Filters:** Remove invalid records (if any)

#### Tables

##### 1. `orders` (Cleaned)

Same schema as Bronze + applied business rules

##### 2. `order_items` (Cleaned)

Same schema as Bronze + validated product references

##### 3. `products` (Enriched)

Same as Bronze (minimal transformation)

##### 4. `units` (Enriched with Geography)

| Column | Type | Description |
|--------|------|-------------|
| `id_unidade` | INT64 | Primary key |
| `nome_unidade` | STRING | Unit name |
| `id_estado` | INT64 | State ID |
| `nome_estado` | STRING | State name (joined) |
| `id_pais` | INT64 | Country ID |
| `nome_pais` | STRING | Country name (joined) |

**Denormalization:** State and country info joined for query performance

---

### Gold Layer (Star Schema + Aggregations)

**Dataset:** `mrhealth_gold`
**Purpose:** Optimized dimensional model for dashboard queries and KPI reporting

#### Star Schema Structure

```
         ┌─────────────┐
         │  dim_date   │
         └──────┬──────┘
                │
      ┌─────────┴─────────┐
      │                   │
┌─────▼──────┐     ┌──────▼────────┐
│ dim_product│◄────┤  fact_sales   │
└────────────┘     └──────▲────────┘
                          │
      ┌───────────────────┴───────────────┐
      │                                   │
┌─────▼──────┐                   ┌────────▼────────┐
│  dim_unit  │                   │ dim_geography   │
└────────────┘                   └─────────────────┘
```

#### Dimension Tables

##### 1. `dim_date` (Type 1 SCD)

**Grain:** One row per calendar date (2025-01-01 to 2027-12-31)
**Rows:** 1,095

| Column | Type | Description |
|--------|------|-------------|
| `date_key` | STRING | Primary key (YYYYMMDD) |
| `full_date` | DATE | Natural key |
| `year` | INT64 | Year (2025-2027) |
| `quarter` | INT64 | Quarter (1-4) |
| `year_quarter` | STRING | "YYYY-QX" |
| `month` | INT64 | Month (1-12) |
| `month_name` | STRING | "January", "February", etc. |
| `year_month` | STRING | "YYYY-MM" |
| `week_of_year` | INT64 | Week number (1-53) |
| `iso_week` | INT64 | ISO week number |
| `day_of_month` | INT64 | Day (1-31) |
| `day_of_week_num` | INT64 | Day number (1=Sunday, 7=Saturday) |
| `day_of_week_name` | STRING | "Monday", "Tuesday", etc. |
| `day_of_week_abbrev` | STRING | "Mon", "Tue", etc. |
| `day_of_year` | INT64 | Day of year (1-366) |
| `is_weekend` | BOOL | TRUE if Saturday/Sunday |
| `is_weekday` | BOOL | TRUE if Monday-Friday |

**Purpose:** Supports time-series analysis, MoM/YoY comparisons, drill-down hierarchies

##### 2. `dim_product` (Type 2 SCD - Ready)

**Grain:** One row per product
**Rows:** 30

| Column | Type | Description |
|--------|------|-------------|
| `product_key` | INT64 | Surrogate key (for SCD Type 2) |
| `product_id` | INT64 | Natural key |
| `product_name` | STRING | Product name |
| `product_price` | NUMERIC(10,2) | Current price |
| `effective_date` | DATE | Price effective date |
| `expiration_date` | DATE | Price expiration date (NULL = current) |
| `is_current` | BOOL | TRUE = current version |

**Purpose:** Track product price history (SCD Type 2 prepared but not yet implemented)

##### 3. `dim_unit` (Type 1 SCD)

**Grain:** One row per restaurant unit
**Rows:** 50 (test: 3)

| Column | Type | Description |
|--------|------|-------------|
| `unit_key` | INT64 | Surrogate key |
| `unit_id` | INT64 | Natural key |
| `unit_name` | STRING | Restaurant name |
| `state_id` | INT64 | State ID |
| `state_name` | STRING | State name (denormalized) |
| `country_id` | INT64 | Country ID |
| `country_name` | STRING | Country name (denormalized) |

**Purpose:** Unit-level analysis, geographic filtering, unit rankings

##### 4. `dim_geography` (Type 1 SCD)

**Grain:** One row per state
**Rows:** 3

| Column | Type | Description |
|--------|------|-------------|
| `geography_key` | INT64 | Surrogate key |
| `state_id` | INT64 | Natural key |
| `state_name` | STRING | State name |
| `country_id` | INT64 | Country ID |
| `country_name` | STRING | Country name |

**Purpose:** Regional aggregations, geographic drill-down

#### Fact Tables

##### 5. `fact_sales`

**Grain:** One row per order
**Rows:** ~5,000/month (test: 15)

| Column | Type | Description | Key Type |
|--------|------|-------------|----------|
| `date_key` | STRING | Date dimension FK | FK |
| `product_key` | INT64 | Product dimension FK | FK |
| `unit_key` | INT64 | Unit dimension FK | FK |
| `geography_key` | INT64 | Geography dimension FK | FK |
| `order_id` | STRING | Order identifier | Degenerate |
| `order_type` | STRING | Online/Physical | Attribute |
| `order_value` | NUMERIC(10,2) | Total order value | Measure |
| `delivery_fee` | NUMERIC(10,2) | Delivery fee | Measure |
| `status` | STRING | Order status | Attribute |
| `delivery_address` | STRING | Delivery address | Attribute |

**Partitioning:** By `date_key` (daily partitions)
**Clustering:** By `unit_key`, `product_key`

**Purpose:** Order-level analytics, revenue tracking, unit performance

##### 6. `fact_order_items`

**Grain:** One row per order line item
**Rows:** ~15,000/month (test: 45)

| Column | Type | Description | Key Type |
|--------|------|-------------|----------|
| `date_key` | STRING | Date dimension FK | FK |
| `product_key` | INT64 | Product dimension FK | FK |
| `unit_key` | INT64 | Unit dimension FK | FK |
| `geography_key` | INT64 | Geography dimension FK | FK |
| `order_id` | STRING | Order identifier | Degenerate |
| `item_id` | STRING | Item identifier | Degenerate |
| `quantity` | INT64 | Quantity purchased | Measure |
| `item_value` | NUMERIC(10,2) | Item unit price | Measure |
| `total_item_value` | NUMERIC(10,2) | Extended price (qty × price) | Measure |
| `observation` | STRING | Customer notes | Attribute |

**Partitioning:** By `date_key`
**Clustering:** By `product_key`, `unit_key`

**Purpose:** Product-level analytics, quantity analysis, basket composition

#### Pre-Aggregation Tables

##### 7. `agg_daily_sales`

**Grain:** One row per date
**Rows:** 1 per day with sales

| Column | Type | Description |
|--------|------|-------------|
| `date_key` | STRING | Date (PK) |
| `full_date` | DATE | Calendar date |
| `total_orders` | INT64 | Order count |
| `total_revenue` | NUMERIC(12,2) | Sum(order_value) |
| `total_delivery_fees` | NUMERIC(12,2) | Sum(delivery_fee) |
| `avg_order_value` | NUMERIC(10,2) | Revenue / Orders |
| `online_orders` | INT64 | Online order count |
| `physical_orders` | INT64 | Physical order count |
| `online_order_pct` | NUMERIC(5,2) | Online % |
| `physical_order_pct` | NUMERIC(5,2) | Physical % |
| `canceled_orders` | INT64 | Canceled count |
| `cancellation_rate_pct` | NUMERIC(5,2) | Canceled % |

**Purpose:** Executive dashboard KPIs, time-series trending (100x query speedup)

##### 8. `agg_unit_performance`

**Grain:** One row per unit
**Rows:** 50 (test: 3)

| Column | Type | Description |
|--------|------|-------------|
| `unit_key` | INT64 | Unit dimension FK |
| `unit_name` | STRING | Restaurant name |
| `state_name` | STRING | State |
| `total_orders` | INT64 | Order count |
| `total_revenue` | NUMERIC(12,2) | Revenue |
| `avg_order_value` | NUMERIC(10,2) | AOV |
| `online_order_pct` | NUMERIC(5,2) | Online % |
| `cancellation_rate_pct` | NUMERIC(5,2) | Cancel rate |
| `active_days` | INT64 | Days with sales |
| `revenue_rank` | INT64 | Revenue ranking |

**Purpose:** Unit rankings, unit comparison, performance heat maps

##### 9. `agg_product_performance`

**Grain:** One row per product
**Rows:** 30

| Column | Type | Description |
|--------|------|-------------|
| `product_key` | INT64 | Product dimension FK |
| `product_name` | STRING | Product name |
| `total_quantity_sold` | INT64 | Units sold |
| `total_revenue` | NUMERIC(12,2) | Revenue |
| `avg_item_price` | NUMERIC(10,2) | Average price |
| `order_count` | INT64 | Orders containing product |
| `unit_penetration` | INT64 | Units selling product |
| `unit_penetration_pct` | NUMERIC(5,2) | Penetration % |

**Purpose:** Product analysis, top products, penetration metrics

---

## 🔄 Data Flow

```
┌──────────────────┐
│ Unit POS System  │
│ (50 units)       │
└────────┬─────────┘
         │ Daily CSV Export
         ▼
┌──────────────────────────────────┐
│ GCS Bucket                       │
│ gs://mrhealth-datalake-485810/   │
│   └─ raw/csv_sales/YYYY/MM/DD/   │
└────────┬─────────────────────────┘
         │ File Upload Event
         ▼
┌──────────────────────────────────┐
│ Cloud Function: csv-processor    │
│ • Validate schema                │
│ • Convert types (Decimal)        │
│ • Deduplicate                    │
│ • Add metadata                   │
└────────┬─────────────────────────┘
         │ < 3 minutes
         ▼
┌──────────────────────────────────┐
│ BigQuery Bronze Layer            │
│ • Raw + schema enforced          │
│ • Partitioned by _ingest_date    │
└────────┬─────────────────────────┘
         │ SQL Transform (daily)
         ▼
┌──────────────────────────────────┐
│ BigQuery Silver Layer            │
│ • Cleaned + enriched             │
│ • Business rules applied         │
└────────┬─────────────────────────┘
         │ SQL Transform (daily)
         ▼
┌──────────────────────────────────┐
│ BigQuery Gold Layer              │
│ • Star schema                    │
│ • Dimensions + Facts             │
│ • Pre-aggregations               │
└────────┬─────────────────────────┘
         │ < 5 seconds
         ▼
┌──────────────────────────────────┐
│ Looker Studio Dashboards         │
│ • Executive                      │
│ • Operations                     │
│ • Pipeline Monitor               │
└──────────────────────────────────┘
```

---

## 🐍 Scripts & Execution Order

### Deployment Scripts (One-Time)

| Script | Purpose | Execution Order | Prerequisites |
|--------|---------|-----------------|---------------|
| `deploy_phase1_infrastructure.py` | Create BigQuery datasets and tables | 1 | GCP project, gcloud auth |
| `load_reference_data.py` | Load product/unit/state/country reference data | 2 | Bronze tables exist |
| `verify_infrastructure.py` | Validate infrastructure setup | 3 | Tables loaded |

**Commands:**
```bash
# 1. Deploy infrastructure
python scripts/deploy_phase1_infrastructure.py

# 2. Load reference data
python scripts/load_reference_data.py

# 3. Verify setup
python scripts/verify_infrastructure.py
```

### Data Generation Scripts (Testing)

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `generate_fake_sales.py` | Generate test CSV files | Testing/demo |
| `upload_fake_data_to_gcs.py` | Upload CSVs to GCS bucket | Testing/demo |

**Commands:**
```bash
# Generate test data
python scripts/generate_fake_sales.py --units 50 --days 30

# Upload to GCS (triggers Cloud Function)
python scripts/upload_fake_data_to_gcs.py
```

### Transformation Scripts (Daily)

| Script | Purpose | Execution Order | Input | Output |
|--------|---------|-----------------|-------|--------|
| `build_silver_layer.py` | Transform Bronze → Silver | 1 | Bronze tables | Silver tables |
| `build_gold_layer.py` | Transform Silver → Gold | 2 | Silver tables | Gold dimensions & facts |
| `build_aggregations.py` | Build KPI aggregation tables | 3 | Gold facts | Gold aggregations |

**Commands:**
```bash
# Daily transformation pipeline
python scripts/build_silver_layer.py
python scripts/build_gold_layer.py
python scripts/build_aggregations.py
```

**Timing:**
- Silver: ~30 seconds
- Gold: ~45 seconds
- Aggregations: ~15 seconds
- **Total:** < 2 minutes

---

## 📊 SQL Transformations

### Bronze DDL

| File | Purpose | Tables Created |
|------|---------|----------------|
| `sql/bronze/create_tables.sql` | Create Bronze layer tables | 6 tables (orders, order_items, products, units, states, countries) |

### Silver Transformations

| File | Purpose | Source | Target |
|------|---------|--------|--------|
| `sql/silver/01_reference_tables.sql` | Clean reference data | Bronze reference | Silver reference |
| `sql/silver/02_orders.sql` | Clean & enrich orders | Bronze orders | Silver orders |
| `sql/silver/03_order_items.sql` | Clean & validate items | Bronze order_items | Silver order_items |

**Key Transformations:**
- Null handling with COALESCE
- Business rule enforcement (physical orders)
- Reference data joins
- Data type conversions

### Gold Transformations

| File | Purpose | Type | Grain |
|------|---------|------|-------|
| `sql/gold/01_dim_date.sql` | Build date dimension | Dimension | One row per date (1,095 rows) |
| `sql/gold/02_dim_product.sql` | Build product dimension | Dimension | One row per product (30 rows) |
| `sql/gold/03_dim_unit.sql` | Build unit dimension | Dimension | One row per unit (50 rows) |
| `sql/gold/04_dim_geography.sql` | Build geography dimension | Dimension | One row per state (3 rows) |
| `sql/gold/05_fact_sales.sql` | Build sales fact | Fact | One row per order |
| `sql/gold/06_fact_order_items.sql` | Build items fact | Fact | One row per line item |
| `sql/gold/07_agg_daily_sales.sql` | Daily KPI aggregations | Aggregation | One row per date |
| `sql/gold/08_agg_unit_performance.sql` | Unit performance metrics | Aggregation | One row per unit |
| `sql/gold/09_agg_product_performance.sql` | Product performance metrics | Aggregation | One row per product |

**Key Features:**
- Star schema joins (fact → dimensions)
- Surrogate key generation
- Partitioning & clustering for performance
- Pre-aggregations for dashboard speedup (100x)

---

## 📈 Data Quality & Monitoring

### Data Quality Checks

**Referential Integrity:**
```sql
-- Check for orphaned order items (should return 0)
SELECT COUNT(*) AS orphaned_items
FROM `mrhealth_bronze.order_items` oi
LEFT JOIN `mrhealth_bronze.orders` o ON oi.id_pedido = o.id_pedido
WHERE o.id_pedido IS NULL;
```

**Data Freshness:**
```sql
-- Check last ingestion (should be < 2 days)
SELECT
  MAX(_ingest_date) AS last_ingest_date,
  DATE_DIFF(CURRENT_DATE(), MAX(_ingest_date), DAY) AS days_since_last_ingest
FROM `mrhealth_bronze.orders`;
```

**Business Rule Validation:**
```sql
-- Physical orders should have zero delivery fee
SELECT COUNT(*) AS violations
FROM `mrhealth_silver.orders`
WHERE tipo_pedido = 'Loja Fisica'
  AND taxa_entrega != 0.00;
```

### Monitoring Queries

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete monitoring and alerting queries.

---

## 🎯 Quick Reference

### Key Metrics (Test Data)

| Metric | Value |
|--------|-------|
| **Orders (Bronze)** | 0 rows (awaiting batch upload) |
| **Orders (Silver)** | 15 rows |
| **Orders (Gold)** | 15 rows |
| **Order Items** | 45 rows |
| **Revenue** | $2,784.17 |
| **Average Order Value** | $185.61 |
| **Online Orders** | 26.7% |
| **Cancellation Rate** | 6.7% |

### File Locations

| Component | Path |
|-----------|------|
| **Bronze DDL** | `sql/bronze/create_tables.sql` |
| **Silver SQL** | `sql/silver/*.sql` (3 files) |
| **Gold SQL** | `sql/gold/*.sql` (9 files) |
| **Python Scripts** | `scripts/*.py` (9 files) |
| **Test Data** | `output/csv_sales/` and `output/reference_data/` |
| **Config** | `config/project_config.yaml` |

---

**Last Updated:** 2026-01-29
**Author:** DataLakers Engineering Team
