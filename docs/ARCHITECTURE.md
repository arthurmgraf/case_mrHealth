# Case Fictício - Teste Data Platform - Architecture Documentation

**Comprehensive Technical Architecture**

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Design Principles](#design-principles)
3. [Layer-by-Layer Architecture](#layer-by-layer-architecture)
4. [Data Models](#data-models)
5. [Security & Access Control](#security--access-control)
6. [Performance Optimization](#performance-optimization)
7. [Disaster Recovery](#disaster-recovery)
8. [Monitoring & Observability](#monitoring--observability)

---

## System Overview

### Architecture Pattern

**Medallion Architecture** (Databricks/Lakehouse standard)

```
Raw Data → Bronze (Schema-on-Write) → Silver (Cleaned) → Gold (Analytics)
```

**Benefits:**
- Clear data quality progression
- Replayability (raw data preserved)
- Incremental improvements without starting over
- Industry-standard pattern

### Technology Decisions

| Decision | Technology | Alternative Considered | Rationale |
|----------|------------|----------------------|-----------|
| Storage | Cloud Storage + BigQuery | Snowflake, Redshift | GCP Free Tier, no egress costs |
| Ingestion | Cloud Functions | Dataproc (Spark) | $0 vs $50/month, sufficient for 500 KB/day |
| Transformation | BigQuery SQL | Dataform, dbt | Simpler for MVP, easy upgrade path |
| Orchestration | GCS Event Triggers | Cloud Composer | $0 vs $300/month, sufficient for event-driven |
| Visualization | Looker Studio | Tableau, Power BI | $0 vs $15-70/user/month, native GCP |

---

## Design Principles

### 1. Cost Optimization

**Target: $0.00/month**

- Use GCP Free Tier services exclusively
- Serverless architecture (no always-on compute)
- Event-driven (no polling loops)
- Pre-aggregated tables for dashboard performance

### 2. Scalability

**Current: 50 units, 163 orders/day**
**Target: 500 units, 1,630 orders/day** (within free tier)

Upgrade path:
```
50 units → 500 units: No changes needed
500 units → 5,000 units: Cloud Run + Pub/Sub
5,000+ units: Dataflow + Dataform
```

### 3. Data Quality

**Validation Layers:**

1. **Cloud Function (Ingestion):**
   - Schema validation
   - Null handling
   - Type casting
   - Deduplication
   - Quarantine invalid files

2. **Silver Layer (Transformation):**
   - Business rule enforcement
   - Referential integrity (INNER JOIN)
   - Date enrichment
   - Calculated fields

3. **Gold Layer (Analytics):**
   - Aggregation consistency
   - Dimension conformance
   - KPI definitions

### 4. Observability

**Monitoring Points:**

- Cloud Function logs (ingestion success/failure)
- BigQuery job statistics (bytes processed, execution time)
- Dashboard query performance (< 5 sec SLA)
- Data freshness (_ingest_date field)

---

## Layer-by-Layer Architecture

### Phase 1: Foundation (Infrastructure)

**Components:**
- GCP Project: `sixth-foundry-485810-e5`
- GCS Bucket: `gs://case_ficticio-datalake-485810/`
- BigQuery Datasets: `case_ficticio_bronze`, `case_ficticio_silver`, `case_ficticio_gold`, `case_ficticio_monitoring`

**Setup Time:** 15 minutes
**Cost:** $0.00

### Phase 2: Ingestion Layer

#### Cloud Function: `csv-processor`

**Trigger:** GCS file upload to `raw/csv_sales/*.csv`

**Processing Logic:**

```python
1. Read CSV from GCS (pandas)
2. Validate schema (columns present, types correct)
3. Clean data:
   - Cast numeric columns to Decimal (BigQuery NUMERIC compatibility)
   - Parse dates
   - Handle nulls
4. Apply business rules:
   - Status in ['Finalizado', 'Pendente', 'Cancelado']
   - Order type in ['Loja Online', 'Loja Fisica']
5. Deduplicate (id_pedido, id_item_pedido)
6. Add metadata:
   - _source_file: Original file path
   - _ingest_timestamp: Processing time
   - _ingest_date: Partition key
7. Load to BigQuery Bronze (WRITE_APPEND)
```

**Error Handling:**
- Invalid files → quarantine bucket with error JSON
- Transient errors → Cloud Functions automatic retry (3x)
- Permanent errors → logged to Cloud Logging

**Performance:**
- Execution time: ~2 seconds/file
- Memory: 256 MB
- Timeout: 300 seconds (5 minutes)

### Phase 3: Transformation Layer

#### Bronze Layer

**Purpose:** Schema-on-write, preserve raw data

**Tables:**

| Table | Rows | Partition | Purpose |
|-------|------|-----------|---------|
| `orders` | ~5K/month | _ingest_date | Order headers |
| `order_items` | ~15K/month | _ingest_date | Line items |
| `products` | 30 | None | Product catalog |
| `units` | 3 | None | Store locations |
| `states` | 3 | None | Geography |
| `countries` | 1 | None | Geography |

**Partitioning Strategy:**

```sql
-- Orders and order_items partitioned by _ingest_date
PARTITION BY _ingest_date

-- Benefits:
-- - Query pruning (scan only relevant dates)
-- - Cost reduction (BigQuery charges per byte scanned)
-- - Faster queries (less data to scan)
```

#### Silver Layer

**Purpose:** Cleaned, enriched, business-ready

**Transformations:**

1. **Type Normalization:**
   ```sql
   CASE
     WHEN UPPER(tipo_pedido) LIKE '%ONLINE%' THEN 'ONLINE'
     WHEN UPPER(tipo_pedido) LIKE '%FISIC%' THEN 'PHYSICAL'
   END AS order_type
   ```

2. **Date Enrichment:**
   ```sql
   EXTRACT(YEAR FROM order_date) AS order_year,
   EXTRACT(MONTH FROM order_date) AS order_month,
   FORMAT_DATE('%A', order_date) AS order_day_of_week
   ```

3. **Calculated Fields:**
   ```sql
   ROUND(vlr_pedido - taxa_entrega, 2) AS items_subtotal,
   ROUND(qtd * vlr_item, 2) AS total_item_value
   ```

4. **Deduplication:**
   ```sql
   QUALIFY ROW_NUMBER() OVER (
     PARTITION BY id_pedido
     ORDER BY _ingest_timestamp DESC
   ) = 1
   ```

5. **Geography Enrichment:**
   ```sql
   -- Units joined with states and countries
   LEFT JOIN states ON units.id_estado = states.id_estado
   LEFT JOIN countries ON states.id_pais = countries.id_pais
   ```

#### Gold Layer

**Purpose:** Star schema for analytics (Kimball methodology)

**Dimensional Model:**

```
          dim_date
             |
             |
fact_sales --|-- dim_unit
             |
             |-- dim_product (via fact_order_items)
```

**Dimension Tables:**

1. **dim_date** (1,095 rows: 2025-2027)
   - Date spine with full calendar attributes
   - Grain: One row per day
   - Attributes: year, quarter, month, week, day, is_weekend
   - Used for time-based analysis and trending

2. **dim_product** (30 rows)
   - Product catalog
   - Grain: One row per product
   - SCD Type 2 structure (prepared for future)

3. **dim_unit** (3 rows)
   - Store locations with geography denormalized
   - Grain: One row per unit
   - Includes state and country for performance

4. **dim_geography** (3 rows)
   - State-country hierarchy
   - Grain: One row per state
   - Normalized geography dimension

**Fact Tables:**

1. **fact_sales** (Order-level grain)
   - Partitioned by `order_date`
   - Clustered by `unit_key`, `order_type`
   - Additive measures: order_value, delivery_fee, items_subtotal
   - Semi-additive: total_items, distinct_products

2. **fact_order_items** (Line-level grain)
   - Partitioned by `order_date`
   - Clustered by `product_key`
   - Additive measures: quantity, total_item_value
   - Non-additive: unit_price

**Aggregation Tables:**

Pre-aggregated for dashboard performance:

1. **agg_daily_sales** (Daily grain)
   - Total orders, revenue, avg order value
   - Channel mix (online vs physical)
   - Status distribution
   - Active units count

2. **agg_unit_performance** (Unit grain)
   - Revenue and order volume rankings
   - Cancellation rates
   - Date range (first/last order)

3. **agg_product_performance** (Product grain)
   - Revenue and volume rankings
   - Unit penetration (% of units selling)
   - Average pricing

### Phase 4: Consumption Layer

#### Looker Studio Dashboards

**Architecture:**

```
Looker Studio (Browser)
     ↓
  (HTTPS Query)
     ↓
BigQuery Gold Layer
     ↓
  (Result Set)
     ↓
Looker Studio (Render)
```

**Performance Optimization:**

1. **Use Aggregation Tables:**
   - Dashboards query `agg_*` tables, not raw facts
   - 100x faster (pre-aggregated)
   - 10x cheaper (fewer bytes scanned)

2. **Data Caching:**
   - Looker Studio caches query results for 12 hours
   - Reduces BigQuery queries by 90%

3. **Date Filters:**
   - Default: Last 30 days
   - Reduces data scanned by 90%

**Dashboard Types:**

1. **Executive (CEO):**
   - Query pattern: Summarize by date, state
   - Data source: `agg_daily_sales`
   - Refresh: On-demand (user-driven)

2. **Operations (COO):**
   - Query pattern: Rank by unit, product
   - Data source: `agg_unit_performance`, `agg_product_performance`
   - Refresh: On-demand

3. **Pipeline Monitor (IT):**
   - Query pattern: Freshness checks, volume counts
   - Data source: `fact_sales` (custom queries)
   - Refresh: Auto-refresh every 15 minutes

---

## Data Models

### Entity-Relationship Diagram (ERD)

```
┌─────────────┐
│  countries  │
│  (1 row)    │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────┴──────┐
│   states    │
│   (3 rows)  │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────┴──────┐       ┌─────────────┐
│    units    │──────▶│   orders    │
│   (3 rows)  │ 1   N │ (5K/month)  │
└─────────────┘       └──────┬──────┘
                             │ 1
                             │
                             │ N
                      ┌──────┴──────────┐
                      │  order_items    │◀─────┐
                      │  (15K/month)    │      │
                      └─────────────────┘      │ N
                                               │
                                          ┌────┴─────┐
                                          │ products │
                                          │ (30 rows)│
                                          └──────────┘
```

### Star Schema (Gold Layer)

```
                ┌───────────────┐
                │   dim_date    │
                │  (1,095 rows) │
                └───────┬───────┘
                        │
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────┴────────┐ ┌───┴────────┐ ┌────┴───────────┐
│  dim_product   │ │ fact_sales │ │   dim_unit     │
│   (30 rows)    │ │(5K/month)  │ │   (3 rows)     │
└────────────────┘ └────┬───────┘ └────────────────┘
                        │
                        │
              ┌─────────┴──────────┐
              │ fact_order_items   │
              │   (15K/month)      │
              └────────────────────┘
```

### Column-Level Lineage

**Example: order_value in fact_sales**

```
Source CSV (pedido.csv)
  Vlr_Pedido (float)
     ↓
Cloud Function (main.py)
  Convert to Decimal (line 153)
     ↓
Bronze Table (orders)
  vlr_pedido (NUMERIC)
     ↓
Silver Transformation (02_orders.sql)
  ROUND(vlr_pedido, 2) AS order_value
     ↓
Gold Fact Table (05_fact_sales.sql)
  order_value (NUMERIC)
     ↓
Aggregation Table (07_agg_daily_sales.sql)
  SUM(order_value) AS total_revenue
     ↓
Looker Studio Dashboard
  Total Revenue MTD (Scorecard)
```

---

## Security & Access Control

### IAM Roles

| Service Account | Role | Purpose |
|-----------------|------|---------|
| Cloud Function default | `roles/bigquery.dataEditor` | Write to Bronze tables |
| Cloud Function default | `roles/storage.objectViewer` | Read CSV files from GCS |
| User | `roles/bigquery.user` | Run queries, view data |
| Looker Studio | Auto-granted | Query BigQuery on behalf of user |

### Data Access Control

**Row-Level Security (Future):**

```sql
-- Example: Restrict unit managers to their unit's data
CREATE ROW ACCESS POLICY unit_access_policy
ON case_ficticio_gold.fact_sales
GRANT TO ('unit_manager@case_ficticio.com')
FILTER USING (unit_key = SESSION_USER().unit_id);
```

**Column-Level Security (Future):**

```sql
-- Example: Hide delivery addresses from operations team
GRANT SELECT (order_id, unit_key, order_value, order_status)
ON case_ficticio_gold.fact_sales
TO GROUP operations_team;
```

### Data Encryption

- **At Rest:** BigQuery automatic encryption (AES-256)
- **In Transit:** HTTPS for all GCS/BigQuery communication
- **Client-Side:** Not required (no PII/sensitive data)

---

## Performance Optimization

### BigQuery Optimization

1. **Partitioning:**
   - All fact tables partitioned by date
   - 100x faster queries with date filters
   - 100x cheaper (only scan relevant partitions)

2. **Clustering:**
   - `fact_sales` clustered by `unit_key`, `order_type`
   - `fact_order_items` clustered by `product_key`
   - Optimal for dashboard queries (group by unit, product)

3. **Table Expiration (Future):**
   ```sql
   -- Auto-delete old Bronze data (keep 90 days)
   ALTER TABLE case_ficticio_bronze.orders
   SET OPTIONS (partition_expiration_days=90);
   ```

4. **Materialized Views (Future):**
   ```sql
   -- Auto-refresh aggregations
   CREATE MATERIALIZED VIEW case_ficticio_gold.agg_daily_sales AS
   SELECT ... FROM fact_sales GROUP BY order_date;
   ```

### Cloud Function Optimization

1. **Cold Start Reduction:**
   - Keep function warm with Cloud Scheduler ping (if needed)
   - Current: < 3 second cold start acceptable

2. **Memory Allocation:**
   - 256 MB sufficient for 5 KB CSVs
   - Upgrade to 512 MB if files > 50 KB

3. **Concurrency:**
   - Max concurrent: 100 (default)
   - Current: 1-2 concurrent (sufficient)

---

## Disaster Recovery

### Backup Strategy

1. **Raw Data:**
   - GCS bucket: 30-day object retention policy
   - Can replay from raw if Bronze corrupted

2. **Bronze Layer:**
   - BigQuery automatic backups (7-day time travel)
   ```sql
   -- Restore from 2 days ago
   SELECT * FROM `case_ficticio_bronze.orders`
   FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY);
   ```

3. **Silver/Gold:**
   - Rebuil dable from Bronze via SQL scripts
   - No backup needed (can regenerate in 5 minutes)

### Recovery Time Objective (RTO)

| Component | Failure Mode | Recovery Time | Recovery Procedure |
|-----------|--------------|---------------|-------------------|
| Cloud Function | Code bug | 5 minutes | Redeploy previous version |
| Bronze Table | Data corruption | 15 minutes | Time-travel restore |
| Silver/Gold | Schema change | 5 minutes | Re-run transformation scripts |
| Dashboard | Deleted | 10 minutes | Recreate from saved JSON |

---

## Monitoring & Observability

### Cloud Logging

**Function Logs:**
```bash
# View recent ingestion logs
gcloud functions logs read csv-processor --gen2 --region=us-central1 --limit=50

# Filter for errors
gcloud functions logs read csv-processor --gen2 --region=us-central1 \
  --filter="severity=ERROR"
```

**BigQuery Job Logs:**
```sql
-- Query execution stats (last 7 days)
SELECT
  user_email,
  job_type,
  COUNT(*) AS job_count,
  ROUND(SUM(total_bytes_processed) / 1e9, 2) AS gb_processed,
  ROUND(AVG(total_slot_ms) / 1000, 2) AS avg_seconds
FROM `sixth-foundry-485810-e5.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY user_email, job_type
ORDER BY gb_processed DESC;
```

### Free Tier Monitoring

```sql
-- Daily BigQuery usage
SELECT
  DATE(creation_time) AS query_date,
  ROUND(SUM(total_bytes_processed) / 1e12, 4) AS tb_processed,
  ROUND(SUM(total_bytes_billed) / 1e12, 4) AS tb_billed
FROM `sixth-foundry-485810-e5.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY query_date
ORDER BY query_date DESC;

-- Free tier limit: 1 TB/month
-- Alert if approaching 800 GB
```

### Data Quality Monitoring

```sql
-- Data freshness check
SELECT
  MAX(_ingest_date) AS last_ingest_date,
  DATE_DIFF(CURRENT_DATE(), MAX(_ingest_date), DAY) AS days_since_last_ingest
FROM `sixth-foundry-485810-e5.case_ficticio_bronze.orders`;

-- Alert if > 2 days
```

```sql
-- Referential integrity check
SELECT
  COUNT(*) AS orphaned_items
FROM `sixth-foundry-485810-e5.case_ficticio_bronze.order_items` oi
LEFT JOIN `sixth-foundry-485810-e5.case_ficticio_bronze.orders` o
  ON oi.id_pedido = o.id_pedido
WHERE o.id_pedido IS NULL;

-- Alert if > 0
```

---

## Appendix

### Glossary

- **Medallion Architecture:** Data engineering pattern with Bronze (raw), Silver (clean), Gold (analytics) layers
- **Star Schema:** Dimensional modeling with fact tables (metrics) and dimension tables (context)
- **SCD Type 2:** Slowly Changing Dimension tracking historical changes
- **Kimball Methodology:** Dimensional modeling approach for data warehouses
- **Free Tier:** GCP services with no-cost usage limits

### References

- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Looker Studio Help](https://support.google.com/looker-studio)
- [Medallion Architecture (Databricks)](https://www.databricks.com/glossary/medallion-architecture)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-29
**Author:** Arthur Graf Architecture Team
