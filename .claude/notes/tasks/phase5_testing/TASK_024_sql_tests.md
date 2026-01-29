# TASK_024: BigQuery SQL Tests

## Description

Create SQL-based tests that validate the Silver and Gold layer transformations. Tests verify row counts, data consistency, referential integrity, and business rule application. Tests run as BigQuery queries.

## Prerequisites

- TASK_014-015 complete (Silver and Gold layers exist)
- Test data loaded through the pipeline

## Test Queries

Create `tests/sql/test_silver_transforms.sql`:

```sql
-- =============================================================
-- SILVER LAYER TESTS
-- Execute after Silver layer refresh
-- Expected: all tests return 'PASS'
-- =============================================================

-- TEST 1: Silver orders row count > 0
SELECT
  'T01_silver_orders_not_empty' AS test_name,
  CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`;

-- TEST 2: Silver order types are normalized
SELECT
  'T02_order_types_normalized' AS test_name,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`
WHERE order_type NOT IN ('ONLINE', 'PHYSICAL', 'UNKNOWN');

-- TEST 3: No null order IDs
SELECT
  'T03_no_null_order_ids' AS test_name,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`
WHERE order_id IS NULL;

-- TEST 4: Items have calculated total
SELECT
  'T04_items_total_calculated' AS test_name,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items`
WHERE total_item_value IS NULL OR total_item_value <= 0;

-- TEST 5: Units enriched with state name
SELECT
  'T05_units_have_state' AS test_name,
  CASE WHEN COUNTIF(state_name IS NULL) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNTIF(state_name IS NULL) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_silver.units`;

-- TEST 6: Silver preserves or reduces row count (no duplication)
SELECT
  'T06_no_row_inflation' AS test_name,
  CASE WHEN silver_count <= bronze_count THEN 'PASS' ELSE 'FAIL' END AS result,
  bronze_count - silver_count AS detail
FROM (
  SELECT
    (SELECT COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`) AS bronze_count,
    (SELECT COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`) AS silver_count
);
```

Create `tests/sql/test_gold_models.sql`:

```sql
-- =============================================================
-- GOLD LAYER TESTS
-- Execute after Gold layer refresh
-- Expected: all tests return 'PASS'
-- =============================================================

-- TEST 1: dim_date covers expected range
SELECT
  'T07_dim_date_range' AS test_name,
  CASE
    WHEN MIN(full_date) <= '2025-01-01' AND MAX(full_date) >= '2027-12-31'
    THEN 'PASS' ELSE 'FAIL'
  END AS result,
  CONCAT(CAST(MIN(full_date) AS STRING), ' to ', CAST(MAX(full_date) AS STRING)) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_gold.dim_date`;

-- TEST 2: All fact_sales have valid date keys
SELECT
  'T08_valid_date_keys' AS test_name,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales` f
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_date` d ON f.date_key = d.date_key
WHERE d.date_key IS NULL;

-- TEST 3: All fact_sales have valid unit keys
SELECT
  'T09_valid_unit_keys' AS test_name,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales` f
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_gold.dim_unit` u ON f.unit_key = u.unit_key
WHERE u.unit_key IS NULL;

-- TEST 4: Revenue consistency between Silver and Gold
SELECT
  'T10_revenue_consistency' AS test_name,
  CASE
    WHEN ABS(gold_revenue - silver_revenue) < 1.0 THEN 'PASS'
    ELSE 'FAIL'
  END AS result,
  ROUND(ABS(gold_revenue - silver_revenue), 2) AS detail
FROM (
  SELECT
    (SELECT SUM(order_value) FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales`) AS gold_revenue,
    (SELECT SUM(order_value) FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`) AS silver_revenue
);

-- TEST 5: KPI aggregation not empty
SELECT
  'T11_daily_agg_not_empty' AS test_name,
  CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_gold.agg_daily_sales`;

-- TEST 6: Product dimension matches catalog
SELECT
  'T12_product_dim_complete' AS test_name,
  CASE WHEN COUNT(*) = 30 THEN 'PASS' ELSE 'FAIL' END AS result,
  COUNT(*) AS detail
FROM `case_ficticio-data-mvp.case_ficticio_gold.dim_product`;
```

### Running SQL Tests

```bash
# Run Silver tests
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp --format=prettyjson < tests/sql/test_silver_transforms.sql

# Run Gold tests
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp --format=prettyjson < tests/sql/test_gold_models.sql
```

## Acceptance Criteria

- [ ] All Silver tests return PASS
- [ ] All Gold tests return PASS
- [ ] Tests execute in under 30 seconds
- [ ] Tests scan minimal data (< 100 MB each)

## Cost Impact

| Action | Cost |
|--------|------|
| SQL test queries (~200 MB total) | Free (within 1 TB/month) |
| **Total** | **$0.00** |

---

*TASK_024 of 26 -- Phase 5: Testing*
