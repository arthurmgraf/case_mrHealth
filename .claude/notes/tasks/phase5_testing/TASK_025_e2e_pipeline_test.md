# TASK_025: End-to-End Pipeline Test

## Description

Execute a complete end-to-end test of the Case Fictício - Teste data pipeline: generate fake data, upload to GCS, trigger Cloud Function processing, run Silver and Gold transformations, and validate final dashboard data. This test proves the entire system works within free tier limits.

## Prerequisites

- All Phase 1-4 tasks complete
- TASK_023-024 tests passing

## E2E Test Script

Create `tests/integration/test_e2e_pipeline.py`:

```python
#!/usr/bin/env python3
"""
Case Fictício - Teste -- End-to-End Pipeline Test
=======================================

Runs the complete pipeline:
1. Generate fake data (3 units, 2 days)
2. Upload to GCS
3. Wait for Cloud Function processing
4. Run Silver transformations
5. Run Gold transformations
6. Validate final state

Usage:
    python tests/integration/test_e2e_pipeline.py
"""

import subprocess
import time
import sys
from datetime import datetime, timedelta
from google.cloud import bigquery, storage

PROJECT = "case_ficticio-data-mvp"
BUCKET = "case_ficticio-data-lake-mvp"


def step(name: str):
    print(f"\n{'='*60}")
    print(f"STEP: {name}")
    print(f"{'='*60}")


def run_cmd(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  [ERROR] {result.stderr}")
        sys.exit(1)
    return result


def wait_for_processing(max_wait: int = 300, check_interval: int = 15):
    """Wait for Cloud Function to process uploaded files."""
    print(f"  Waiting up to {max_wait}s for Cloud Function processing...")
    client = bigquery.Client(project=PROJECT)

    start = time.time()
    while time.time() - start < max_wait:
        query = f"""
        SELECT COUNT(*) as cnt
        FROM `{PROJECT}.case_ficticio_bronze.orders`
        WHERE _ingest_date = CURRENT_DATE()
        """
        result = list(client.query(query).result())
        count = result[0].cnt if result else 0

        if count > 0:
            print(f"  [OK] Found {count} rows in Bronze orders")
            return True

        print(f"  ... waiting ({int(time.time() - start)}s elapsed)")
        time.sleep(check_interval)

    print("  [TIMEOUT] No data found in Bronze after maximum wait")
    return False


def validate_layer(dataset: str, tables: list[str]) -> bool:
    """Validate that tables have data."""
    client = bigquery.Client(project=PROJECT)
    all_ok = True

    for table in tables:
        query = f"SELECT COUNT(*) as cnt FROM `{PROJECT}.{dataset}.{table}`"
        result = list(client.query(query).result())
        count = result[0].cnt if result else 0

        status = "OK" if count > 0 else "FAIL"
        if count == 0:
            all_ok = False
        print(f"  [{status}] {dataset}.{table}: {count} rows")

    return all_ok


def main():
    print("=" * 60)
    print("Case Fictício - Teste -- END-TO-END PIPELINE TEST")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Step 1: Generate fake data (small dataset)
    step("1. Generate Fake Data")
    run_cmd("python scripts/generate_fake_sales.py --units 3 --days 2 --min-orders 5 --max-orders 10 --output-dir ./e2e_test_output --seed 42")
    print("  [OK] Fake data generated")

    # Step 2: Upload reference data
    step("2. Upload Reference Data")
    run_cmd("python scripts/load_reference_data.py --source-dir ./e2e_test_output/reference_data")
    print("  [OK] Reference data uploaded")

    # Step 3: Upload sales CSVs to trigger Cloud Function
    step("3. Upload Sales CSVs to GCS")
    run_cmd("python scripts/upload_to_gcs.py --source-dir ./e2e_test_output/csv_sales")
    print("  [OK] Sales CSVs uploaded")

    # Step 4: Wait for Cloud Function processing
    step("4. Wait for Cloud Function Processing")
    if not wait_for_processing():
        print("  [FAIL] Cloud Function did not process files in time")
        sys.exit(1)

    # Step 5: Run Silver transformations
    step("5. Run Silver Transformations")
    for sql_file in ["sql/silver/reference_tables.sql", "sql/silver/orders.sql", "sql/silver/order_items.sql"]:
        run_cmd(f'bq query --use_legacy_sql=false --project_id={PROJECT} < {sql_file}')
    print("  [OK] Silver transformations complete")

    # Step 6: Run Gold transformations
    step("6. Run Gold Transformations")
    for sql_file in ["sql/gold/dim_date.sql", "sql/gold/dim_product.sql", "sql/gold/dim_unit.sql",
                      "sql/gold/dim_geography.sql", "sql/gold/fact_sales.sql",
                      "sql/gold/fact_order_items.sql", "sql/gold/agg_daily_sales.sql",
                      "sql/gold/agg_unit_performance.sql", "sql/gold/agg_product_performance.sql"]:
        run_cmd(f'bq query --use_legacy_sql=false --project_id={PROJECT} < {sql_file}')
    print("  [OK] Gold transformations complete")

    # Step 7: Validate all layers
    step("7. Validate All Layers")

    print("\n  --- Bronze Layer ---")
    bronze_ok = validate_layer("case_ficticio_bronze", ["orders", "order_items", "products", "units", "states", "countries"])

    print("\n  --- Silver Layer ---")
    silver_ok = validate_layer("case_ficticio_silver", ["orders", "order_items", "products", "units", "states", "countries"])

    print("\n  --- Gold Layer ---")
    gold_ok = validate_layer("case_ficticio_gold", [
        "dim_date", "dim_product", "dim_unit", "dim_geography",
        "fact_sales", "fact_order_items",
        "agg_daily_sales", "agg_unit_performance", "agg_product_performance"
    ])

    # Step 8: Run SQL tests
    step("8. Run SQL Tests")
    run_cmd(f'bq query --use_legacy_sql=false --project_id={PROJECT} < tests/sql/test_silver_transforms.sql')
    run_cmd(f'bq query --use_legacy_sql=false --project_id={PROJECT} < tests/sql/test_gold_models.sql')
    print("  [OK] SQL tests executed")

    # Final Summary
    print("\n" + "=" * 60)
    print("E2E TEST RESULTS")
    print("=" * 60)
    all_pass = bronze_ok and silver_ok and gold_ok
    print(f"  Bronze Layer: {'PASS' if bronze_ok else 'FAIL'}")
    print(f"  Silver Layer: {'PASS' if silver_ok else 'FAIL'}")
    print(f"  Gold Layer:   {'PASS' if gold_ok else 'FAIL'}")
    print(f"  Overall:      {'PASS' if all_pass else 'FAIL'}")
    print(f"\nCompleted: {datetime.now().isoformat()}")
    print("=" * 60)

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
```

### Running E2E Test

```bash
# Run full E2E test
python tests/integration/test_e2e_pipeline.py
```

## Acceptance Criteria

- [ ] Fake data generated successfully
- [ ] Reference data loaded into Bronze
- [ ] Sales CSVs uploaded and processed by Cloud Function
- [ ] Silver layer populated with transformed data
- [ ] Gold layer populated with star schema
- [ ] All SQL tests pass
- [ ] Total execution time < 15 minutes
- [ ] Zero cost incurred

## Cost Impact

| Action | Cost |
|--------|------|
| Small test dataset (~30 orders) | Negligible |
| All queries combined (~1 GB) | Free (within 1 TB) |
| **Total** | **$0.00** |

---

*TASK_025 of 26 -- Phase 5: Testing*
