# TASK_018: KPI Aggregation Models

## Description

Create aggregated KPI tables in the Gold layer that power dashboards and alerts. These pre-computed aggregations optimize dashboard performance by avoiding expensive ad-hoc queries. KPIs are designed for the three main personas: CEO (Joao), COO (Ricardo), and IT Manager (Wilson).

## Prerequisites

- TASK_015 complete (Gold star schema exists)

## KPI Models

### Daily Sales Aggregation

Create `sql/gold/agg_daily_sales.sql`:

```sql
-- Gold Layer: Daily Sales KPI Aggregation
-- Powers the Executive and Operations dashboards

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.agg_daily_sales`
PARTITION BY order_date
CLUSTER BY state_name
AS
SELECT
  f.order_date,
  d.year_month,
  d.year_quarter,
  d.day_of_week_name,
  d.is_weekend,
  u.state_name,

  -- Volume KPIs
  COUNT(DISTINCT f.order_id) AS total_orders,
  SUM(f.total_quantity) AS total_items_sold,
  COUNT(DISTINCT f.unit_key) AS active_units,

  -- Revenue KPIs
  SUM(f.order_value) AS total_revenue,
  SUM(f.delivery_fee) AS total_delivery_fees,
  SUM(f.items_subtotal) AS total_items_revenue,
  AVG(f.order_value) AS avg_order_value,

  -- Channel KPIs
  COUNTIF(f.order_type = 'ONLINE') AS online_orders,
  COUNTIF(f.order_type = 'PHYSICAL') AS physical_orders,
  ROUND(SAFE_DIVIDE(COUNTIF(f.order_type = 'ONLINE'), COUNT(*)) * 100, 2) AS online_pct,

  -- Status KPIs
  COUNTIF(f.order_status = 'Finalizado') AS completed_orders,
  COUNTIF(f.order_status = 'Cancelado') AS cancelled_orders,
  COUNTIF(f.order_status = 'Pendente') AS pending_orders,
  ROUND(SAFE_DIVIDE(COUNTIF(f.order_status = 'Cancelado'), COUNT(*)) * 100, 2) AS cancellation_rate,

  -- Average basket
  AVG(f.total_items) AS avg_items_per_order,
  AVG(f.distinct_products) AS avg_products_per_order

FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales` f
JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_date` d ON f.date_key = d.date_key
JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_unit` u ON f.unit_key = u.unit_key
GROUP BY
  f.order_date, d.year_month, d.year_quarter, d.day_of_week_name,
  d.is_weekend, u.state_name;
```

### Unit Performance Aggregation

Create `sql/gold/agg_unit_performance.sql`:

```sql
-- Gold Layer: Unit Performance KPI Aggregation
-- Powers the Unit Comparison dashboard

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.agg_unit_performance` AS
SELECT
  u.unit_key,
  u.unit_name,
  u.state_name,
  d.year_month,

  -- Volume
  COUNT(DISTINCT f.order_id) AS total_orders,
  COUNT(DISTINCT f.order_date) AS active_days,
  ROUND(SAFE_DIVIDE(COUNT(DISTINCT f.order_id), COUNT(DISTINCT f.order_date)), 1) AS avg_orders_per_day,

  -- Revenue
  SUM(f.order_value) AS total_revenue,
  AVG(f.order_value) AS avg_order_value,
  SUM(f.delivery_fee) AS total_delivery_fees,

  -- Channel mix
  ROUND(SAFE_DIVIDE(COUNTIF(f.order_type = 'ONLINE'), COUNT(*)) * 100, 2) AS online_pct,

  -- Quality
  ROUND(SAFE_DIVIDE(COUNTIF(f.order_status = 'Cancelado'), COUNT(*)) * 100, 2) AS cancellation_rate,

  -- Ranking
  RANK() OVER (PARTITION BY d.year_month ORDER BY SUM(f.order_value) DESC) AS revenue_rank,
  RANK() OVER (PARTITION BY d.year_month ORDER BY COUNT(DISTINCT f.order_id) DESC) AS volume_rank

FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales` f
JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_unit` u ON f.unit_key = u.unit_key
JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_date` d ON f.date_key = d.date_key
GROUP BY u.unit_key, u.unit_name, u.state_name, d.year_month;
```

### Product Performance Aggregation

Create `sql/gold/agg_product_performance.sql`:

```sql
-- Gold Layer: Product Performance KPI Aggregation
-- Powers the Product Analysis dashboard

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.agg_product_performance` AS
SELECT
  p.product_key,
  p.product_name,
  d.year_month,

  -- Volume
  SUM(fi.quantity) AS total_quantity_sold,
  COUNT(DISTINCT fi.order_id) AS orders_containing_product,

  -- Revenue
  SUM(fi.total_item_value) AS total_revenue,
  AVG(fi.unit_price) AS avg_selling_price,

  -- Distribution
  COUNT(DISTINCT f.unit_key) AS units_selling_product,

  -- Ranking
  RANK() OVER (PARTITION BY d.year_month ORDER BY SUM(fi.quantity) DESC) AS quantity_rank,
  RANK() OVER (PARTITION BY d.year_month ORDER BY SUM(fi.total_item_value) DESC) AS revenue_rank

FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_order_items` fi
JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_product` p ON fi.product_key = p.product_key
JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_date` d ON fi.date_key = d.date_key
JOIN `case_ficticio-data-mvp.case_ficticio_gold.fact_sales` f ON fi.order_id = f.order_id
GROUP BY p.product_key, p.product_name, d.year_month;
```

## KPI Reference Table

| KPI | Dashboard | Business Owner | Calculation |
|-----|-----------|----------------|-------------|
| Total Revenue | Executive | Joao | SUM(order_value) |
| Avg Order Value | Executive | Joao | AVG(order_value) |
| Online % | Executive | Joao | online_orders / total_orders |
| Cancellation Rate | Operations | Ricardo | cancelled / total |
| Orders per Day per Unit | Operations | Ricardo | total_orders / active_days |
| Top Products by Revenue | Operations | Ricardo | RANK by SUM(total_item_value) |
| Unit Revenue Rank | Operations | Ricardo | RANK by SUM(order_value) |
| Active Units | Pipeline | Wilson | COUNT(DISTINCT unit_key) |

## Execution

```bash
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/agg_daily_sales.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/agg_unit_performance.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/gold/agg_product_performance.sql
```

## Acceptance Criteria

- [ ] agg_daily_sales table created with all KPI columns
- [ ] agg_unit_performance table with rankings
- [ ] agg_product_performance table with rankings
- [ ] KPIs produce non-null values for test data
- [ ] Aggregation queries complete within 10 seconds

## Cost Impact

| Action | Cost |
|--------|------|
| Aggregation queries (~500 MB/day) | Free (within 1 TB/month) |
| Aggregation table storage (~10 MB) | Free (within 10 GB) |
| **Total** | **$0.00** |

---

*TASK_018 of 26 -- Phase 3: Transformation*
