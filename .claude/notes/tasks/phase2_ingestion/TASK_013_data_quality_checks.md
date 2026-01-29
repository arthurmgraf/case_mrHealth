# TASK_013: Data Quality Checks

## Description

Implement data quality validation rules that run during ingestion (TASK_010/011) and as post-load checks in BigQuery. Quality checks cover completeness, accuracy, consistency, and timeliness. Invalid records are quarantined with detailed error reports.

## Prerequisites

- TASK_010-012 complete (ingestion pipeline operational)

## Quality Check Categories

### 1. Completeness Checks (during ingestion)

```python
def check_completeness(df: pd.DataFrame, required_columns: list[str]) -> dict:
    """Check that required columns have no nulls."""
    results = {}
    for col in required_columns:
        null_count = df[col].isnull().sum()
        total = len(df)
        results[col] = {
            "null_count": int(null_count),
            "total_rows": total,
            "completeness_pct": round((1 - null_count / total) * 100, 2) if total > 0 else 0,
            "pass": null_count == 0,
        }
    return results
```

### 2. Accuracy Checks (during ingestion)

```python
def check_accuracy(df_orders: pd.DataFrame) -> dict:
    """Check data accuracy rules."""
    results = {}

    # Rule: Vlr_Pedido must be positive
    invalid = (df_orders["Vlr_Pedido"] <= 0).sum()
    results["positive_order_value"] = {
        "invalid_count": int(invalid),
        "pass": invalid == 0,
    }

    # Rule: Taxa_Entrega should be 0 for Loja Fisica
    physical = df_orders[df_orders["Tipo_Pedido"] == "Loja Fisica"]
    fee_on_physical = (physical["Taxa_Entrega"] > 0).sum()
    results["no_fee_for_physical"] = {
        "invalid_count": int(fee_on_physical),
        "pass": fee_on_physical == 0,
    }

    # Rule: Online orders should have delivery address
    online = df_orders[df_orders["Tipo_Pedido"] == "Loja Online"]
    no_address = (online["Endereco_Entrega"].isna() | (online["Endereco_Entrega"] == "")).sum()
    results["online_has_address"] = {
        "invalid_count": int(no_address),
        "pass": no_address == 0,
    }

    return results
```

### 3. Post-Load BigQuery Quality Checks

```sql
-- Quality Check 1: Daily completeness (all units reported?)
SELECT
  _ingest_date,
  COUNT(DISTINCT id_unidade) as units_reporting,
  50 as expected_units,
  CASE
    WHEN COUNT(DISTINCT id_unidade) = 50 THEN 'PASS'
    WHEN COUNT(DISTINCT id_unidade) >= 45 THEN 'WARNING'
    ELSE 'FAIL'
  END as check_result
FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`
WHERE _ingest_date = CURRENT_DATE()
GROUP BY _ingest_date;

-- Quality Check 2: Order-to-item referential integrity
SELECT
  'orphan_items' as check_name,
  COUNT(*) as orphan_count,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as check_result
FROM `case_ficticio-data-mvp.case_ficticio_bronze.order_items` oi
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_bronze.orders` o
  ON oi.id_pedido = o.id_pedido
WHERE o.id_pedido IS NULL
  AND oi._ingest_date = CURRENT_DATE();

-- Quality Check 3: Duplicate detection
SELECT
  'duplicate_orders' as check_name,
  COUNT(*) as duplicate_count,
  CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as check_result
FROM (
  SELECT id_pedido, COUNT(*) as cnt
  FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`
  WHERE _ingest_date = CURRENT_DATE()
  GROUP BY id_pedido
  HAVING cnt > 1
);

-- Quality Check 4: Value range validation
SELECT
  'order_value_range' as check_name,
  COUNT(*) as out_of_range,
  MIN(vlr_pedido) as min_value,
  MAX(vlr_pedido) as max_value,
  AVG(vlr_pedido) as avg_value,
  CASE
    WHEN MIN(vlr_pedido) > 0 AND MAX(vlr_pedido) < 10000 THEN 'PASS'
    ELSE 'WARNING'
  END as check_result
FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`
WHERE _ingest_date = CURRENT_DATE();

-- Quality Check 5: Data freshness
SELECT
  'data_freshness' as check_name,
  MAX(_ingest_timestamp) as last_ingestion,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_ingest_timestamp), HOUR) as hours_since_last,
  CASE
    WHEN TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_ingest_timestamp), HOUR) <= 24 THEN 'PASS'
    ELSE 'FAIL'
  END as check_result
FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`;
```

### 4. Quality Results Logging

```sql
-- Create quality check results table
CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_monitoring.quality_checks` (
  check_date DATE,
  check_name STRING,
  check_category STRING,    -- completeness, accuracy, consistency, timeliness
  target_table STRING,
  result STRING,            -- PASS, WARNING, FAIL
  details STRING,           -- JSON with check specifics
  check_timestamp TIMESTAMP
);

-- Insert quality check results (run as scheduled query)
INSERT INTO `case_ficticio-data-mvp.case_ficticio_monitoring.quality_checks`
SELECT
  CURRENT_DATE() as check_date,
  'unit_completeness' as check_name,
  'completeness' as check_category,
  'case_ficticio_bronze.orders' as target_table,
  CASE
    WHEN COUNT(DISTINCT id_unidade) >= 50 THEN 'PASS'
    WHEN COUNT(DISTINCT id_unidade) >= 45 THEN 'WARNING'
    ELSE 'FAIL'
  END as result,
  TO_JSON_STRING(STRUCT(
    COUNT(DISTINCT id_unidade) as units_reporting,
    50 as expected_units
  )) as details,
  CURRENT_TIMESTAMP() as check_timestamp
FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`
WHERE _ingest_date = CURRENT_DATE();
```

## Quarantine Structure

```
gs://case_ficticio-data-lake-mvp/quarantine/
|-- 2026/01/28/
|   |-- unit_003/
|   |   |-- pedido.csv                    (original invalid file)
|   |   |-- pedido_error.json             (error report)
|   |-- unit_017/
|       |-- item_pedido.csv
|       |-- item_pedido_error.json
```

Error report format:
```json
{
  "source_file": "raw/csv_sales/2026/01/28/unit_003/pedido.csv",
  "error_type": "validation_failure",
  "errors": [
    "3 rows with null Id_Pedido",
    "1 row with invalid Status: 'Unknown'"
  ],
  "rows_total": 25,
  "rows_valid": 21,
  "rows_rejected": 4,
  "timestamp": "2026-01-29T02:15:30.000Z"
}
```

## Acceptance Criteria

- [ ] Completeness checks verify all required columns have no nulls
- [ ] Accuracy checks validate business rules (positive values, valid statuses)
- [ ] Post-load BigQuery checks detect missing units, orphan items, duplicates
- [ ] Quality results logged to case_ficticio_monitoring.quality_checks
- [ ] Quarantine files include original data and error report JSON
- [ ] All checks run within free tier query limits

## Cost Impact

| Action | Cost |
|--------|------|
| Quality check queries (~100 MB/day) | Free (within 1 TB/month) |
| Monitoring table storage (~1 MB/month) | Free (within 10 GB) |
| **Total** | **$0.00** |

---

*TASK_013 of 26 -- Phase 2: Ingestion*
