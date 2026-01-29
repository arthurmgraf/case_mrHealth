# TASK_017: Data Quality Assertions (SQL)

## Description

Create SQL-based data quality assertions that validate the Silver and Gold layer data after transformations. Assertions check referential integrity, value ranges, completeness, and consistency. Results are logged to the monitoring dataset.

## Prerequisites

- TASK_014-015 complete (Silver and Gold layers exist)

## Quality Assertions

### Silver Layer Assertions

Create `sql/monitoring/silver_assertions.sql`:

```sql
-- =============================================================
-- SILVER LAYER DATA QUALITY ASSERTIONS
-- Run after daily Silver refresh
-- =============================================================

-- Assertion 1: No duplicate order IDs in Silver
SELECT
  'silver_no_duplicate_orders' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM (
  SELECT order_id, COUNT(*) AS cnt
  FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`
  GROUP BY order_id
  HAVING cnt > 1
);

-- Assertion 2: No duplicate order item IDs in Silver
SELECT
  'silver_no_duplicate_items' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM (
  SELECT order_item_id, COUNT(*) AS cnt
  FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items`
  GROUP BY order_item_id
  HAVING cnt > 1
);

-- Assertion 3: All order items reference valid orders
SELECT
  'silver_referential_integrity' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items` oi
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_silver.orders` o
  ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;

-- Assertion 4: Order values are positive
SELECT
  'silver_positive_order_values' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`
WHERE order_value <= 0;

-- Assertion 5: Valid order types only
SELECT
  'silver_valid_order_types' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`
WHERE order_type NOT IN ('ONLINE', 'PHYSICAL');

-- Assertion 6: Valid order statuses only
SELECT
  'silver_valid_statuses' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`
WHERE order_status NOT IN ('Finalizado', 'Pendente', 'Cancelado');

-- Assertion 7: Item total_item_value matches quantity * unit_price
SELECT
  'silver_item_value_consistency' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items`
WHERE ABS(total_item_value - ROUND(quantity * unit_price, 2)) > 0.01;

-- Assertion 8: All products reference valid product catalog
SELECT
  'silver_valid_products' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'WARNING' END AS result,
  COUNT(*) AS violations
FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items` oi
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_silver.products` p
  ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;
```

### Gold Layer Assertions

Create `sql/monitoring/gold_assertions.sql`:

```sql
-- =============================================================
-- GOLD LAYER DATA QUALITY ASSERTIONS
-- Run after daily Gold refresh
-- =============================================================

-- Assertion 1: Fact sales matches silver orders count
SELECT
  'gold_fact_sales_completeness' AS assertion,
  CASE WHEN ABS(gold_count - silver_count) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  ABS(gold_count - silver_count) AS violations
FROM (
  SELECT
    (SELECT COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales`) AS gold_count,
    (SELECT COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`) AS silver_count
);

-- Assertion 2: All units in fact_sales exist in dim_unit
SELECT
  'gold_valid_unit_keys' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales` f
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_unit` u
  ON f.unit_key = u.unit_key
WHERE u.unit_key IS NULL;

-- Assertion 3: All date keys in facts exist in dim_date
SELECT
  'gold_valid_date_keys' AS assertion,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS violations
FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales` f
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_date` d
  ON f.date_key = d.date_key
WHERE d.date_key IS NULL;

-- Assertion 4: Revenue totals are consistent
SELECT
  'gold_revenue_consistency' AS assertion,
  CASE WHEN ABS(fact_total - silver_total) < 1.0 THEN 'PASS' ELSE 'FAIL' END AS result,
  ROUND(ABS(fact_total - silver_total), 2) AS violations
FROM (
  SELECT
    (SELECT SUM(order_value) FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales`) AS fact_total,
    (SELECT SUM(order_value) FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`) AS silver_total
);
```

### Assertion Results Logger

Create `sql/monitoring/log_assertions.sql`:

```sql
-- Log all assertion results to monitoring table
INSERT INTO `case_ficticio-data-mvp.case_ficticio_monitoring.quality_checks`
(check_date, check_name, check_category, target_table, result, details, check_timestamp)

SELECT CURRENT_DATE(), assertion, 'assertion', 'case_ficticio_silver', result,
  TO_JSON_STRING(STRUCT(violations as violation_count)), CURRENT_TIMESTAMP()
FROM (
  -- Include all Silver assertions here as subqueries
  SELECT 'silver_no_duplicate_orders' AS assertion,
    CASE WHEN (SELECT COUNT(*) FROM (SELECT order_id FROM `case_ficticio-data-mvp.case_ficticio_silver.orders` GROUP BY order_id HAVING COUNT(*)>1)) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
    (SELECT COUNT(*) FROM (SELECT order_id FROM `case_ficticio-data-mvp.case_ficticio_silver.orders` GROUP BY order_id HAVING COUNT(*)>1)) AS violations
);
```

## Acceptance Criteria

- [ ] All Silver assertions pass on clean test data
- [ ] All Gold assertions pass on clean test data
- [ ] Assertion results logged to case_ficticio_monitoring.quality_checks
- [ ] Failed assertions clearly identify the violation count
- [ ] SQL files stored in sql/monitoring/ directory

## Cost Impact

| Action | Cost |
|--------|------|
| Assertion queries (~200 MB/day) | Free (within 1 TB/month) |
| Monitoring storage | Free (within 10 GB) |
| **Total** | **$0.00** |

---

*TASK_017 of 26 -- Phase 3: Transformation*
