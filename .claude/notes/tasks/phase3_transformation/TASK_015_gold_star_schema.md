# TASK_015: Gold Star Schema (Dimensional Model)

## Description

Build the Gold layer dimensional model (Star Schema, Kimball methodology) in BigQuery. This creates dimension tables (date, product, unit, geography) and fact tables (sales, order items) optimized for analytical queries and dashboard consumption.

## Prerequisites

- TASK_014 complete (Silver layer populated)

## Dimensional Model Diagram

```
                    +-------------+
                    | dim_date    |
                    |-------------|
                    | date_key PK |
                    | full_date   |
                    | year        |
                    | month       |
                    | day         |
                    | day_of_week |
                    | is_weekend  |
                    +------+------+
                           |
+-------------+    +-------+-------+    +--------------+
| dim_product |    | fact_sales    |    | dim_unit     |
|-------------|    |---------------|    |--------------|
| product_key |----| order_id  PK  |----| unit_key PK  |
| product_id  |    | date_key  FK  |    | unit_id      |
| product_name|    | product_key   |    | unit_name    |
+-------------+    | unit_key  FK  |    | state_name   |
                   | order_type    |    | country_name |
                   | order_value   |    +--------------+
                   | delivery_fee  |
                   | items_subtotal|
                   | order_status  |
                   +-------+-------+
                           |
                   +-------+----------+
                   | fact_order_items  |
                   |------------------|
                   | item_id      PK  |
                   | order_id     FK  |
                   | product_key  FK  |
                   | quantity         |
                   | unit_price       |
                   | total_value      |
                   +------------------+
```

## SQL Definitions

### dim_date

Create `sql/gold/dim_date.sql`:

```sql
-- Gold Layer: Date Dimension
-- Generates a date spine from 2025-01-01 to 2027-12-31

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.dim_date` AS
SELECT
  FORMAT_DATE('%Y%m%d', d) AS date_key,
  d AS full_date,
  EXTRACT(YEAR FROM d) AS year,
  EXTRACT(QUARTER FROM d) AS quarter,
  EXTRACT(MONTH FROM d) AS month,
  FORMAT_DATE('%B', d) AS month_name,
  EXTRACT(WEEK FROM d) AS week_of_year,
  EXTRACT(DAY FROM d) AS day_of_month,
  EXTRACT(DAYOFWEEK FROM d) AS day_of_week_num,
  FORMAT_DATE('%A', d) AS day_of_week_name,
  CASE WHEN EXTRACT(DAYOFWEEK FROM d) IN (1, 7) THEN TRUE ELSE FALSE END AS is_weekend,
  FORMAT_DATE('%Y-%m', d) AS year_month,
  FORMAT_DATE('%Y-Q%Q', d) AS year_quarter
FROM UNNEST(
  GENERATE_DATE_ARRAY('2025-01-01', '2027-12-31', INTERVAL 1 DAY)
) AS d;
```

### dim_product

Create `sql/gold/dim_product.sql`:

```sql
-- Gold Layer: Product Dimension

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.dim_product` AS
SELECT
  product_id AS product_key,
  product_id,
  product_name,
  CURRENT_TIMESTAMP() AS _valid_from,
  TIMESTAMP('9999-12-31') AS _valid_to,
  TRUE AS is_current
FROM `case_ficticio-data-mvp.case_ficticio_silver.products`;
```

### dim_unit

Create `sql/gold/dim_unit.sql`:

```sql
-- Gold Layer: Unit Dimension (denormalized with geography)

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.dim_unit` AS
SELECT
  unit_id AS unit_key,
  unit_id,
  unit_name,
  state_id,
  state_name,
  country_id,
  country_name,
  CURRENT_TIMESTAMP() AS _valid_from,
  TIMESTAMP('9999-12-31') AS _valid_to,
  TRUE AS is_current
FROM `case_ficticio-data-mvp.case_ficticio_silver.units`;
```

### dim_geography

Create `sql/gold/dim_geography.sql`:

```sql
-- Gold Layer: Geography Dimension (State-Country hierarchy)

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.dim_geography` AS
SELECT
  s.state_id AS geography_key,
  s.state_id,
  s.state_name,
  c.country_id,
  c.country_name
FROM `case_ficticio-data-mvp.case_ficticio_silver.states` s
JOIN `case_ficticio-data-mvp.case_ficticio_silver.countries` c
  ON s.country_id = c.country_id;
```

### fact_sales

Create `sql/gold/fact_sales.sql`:

```sql
-- Gold Layer: Sales Fact Table (order-level grain)

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.fact_sales`
PARTITION BY order_date
CLUSTER BY unit_key, order_type
AS
SELECT
  o.order_id,
  FORMAT_DATE('%Y%m%d', o.order_date) AS date_key,
  o.order_date,
  o.unit_id AS unit_key,
  o.order_type,
  o.order_status,

  -- Measures
  o.order_value,
  o.delivery_fee,
  o.items_subtotal,

  -- Item aggregations
  item_agg.total_items,
  item_agg.distinct_products,
  item_agg.total_quantity,

  -- Delivery
  o.delivery_address,

  -- Metadata
  o._ingest_date

FROM `case_ficticio-data-mvp.case_ficticio_silver.orders` o

LEFT JOIN (
  SELECT
    order_id,
    COUNT(*) AS total_items,
    COUNT(DISTINCT product_id) AS distinct_products,
    SUM(quantity) AS total_quantity
  FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items`
  GROUP BY order_id
) item_agg
  ON o.order_id = item_agg.order_id;
```

### fact_order_items

Create `sql/gold/fact_order_items.sql`:

```sql
-- Gold Layer: Order Items Fact Table (item-level grain)

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.fact_order_items`
PARTITION BY order_date
CLUSTER BY product_key
AS
SELECT
  oi.order_item_id AS item_id,
  oi.order_id,
  FORMAT_DATE('%Y%m%d', o.order_date) AS date_key,
  o.order_date,
  o.unit_id AS unit_key,
  oi.product_id AS product_key,

  -- Measures
  oi.quantity,
  oi.unit_price,
  oi.total_item_value,

  -- Context from order
  o.order_type,
  o.order_status,

  -- Descriptive
  oi.observation,

  -- Metadata
  oi._ingest_date

FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items` oi
JOIN `case_ficticio-data-mvp.case_ficticio_silver.orders` o
  ON oi.order_id = o.order_id;
```

## Execution Order

```bash
# Execute Gold transformations in dependency order
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/dim_date.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/dim_product.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/dim_unit.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/dim_geography.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/fact_sales.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/fact_order_items.sql
```

## Verification

```sql
-- Fact table row counts
SELECT 'fact_sales' as tbl, COUNT(*) as rows FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales`
UNION ALL
SELECT 'fact_order_items', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_order_items`
UNION ALL
SELECT 'dim_date', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_gold.dim_date`
UNION ALL
SELECT 'dim_product', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_gold.dim_product`
UNION ALL
SELECT 'dim_unit', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_gold.dim_unit`
UNION ALL
SELECT 'dim_geography', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_gold.dim_geography`;

-- Test a star-schema join (the kind dashboards will run)
SELECT
  d.year_month,
  u.state_name,
  p.product_name,
  COUNT(DISTINCT f.order_id) AS total_orders,
  SUM(f.order_value) AS total_revenue,
  AVG(f.order_value) AS avg_order_value
FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales` f
JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_date` d ON f.date_key = d.date_key
JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_unit` u ON f.unit_key = u.unit_key
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_gold.fact_order_items` fi ON f.order_id = fi.order_id
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_product` p ON fi.product_key = p.product_key
GROUP BY d.year_month, u.state_name, p.product_name
ORDER BY total_revenue DESC
LIMIT 20;
```

## Acceptance Criteria

- [ ] All 4 dimension tables created with expected row counts
- [ ] Both fact tables created with partitioning and clustering
- [ ] Star schema join query returns valid results
- [ ] Foreign key relationships are consistent (no orphan records)
- [ ] Date dimension spans 2025-2027

## Cost Impact

| Action | Cost |
|--------|------|
| CREATE OR REPLACE queries (~1 GB scanned total) | Free (within 1 TB/month) |
| Gold table storage (~30 MB) | Free (within 10 GB) |
| **Total** | **$0.00** |

---

*TASK_015 of 26 -- Phase 3: Transformation*
