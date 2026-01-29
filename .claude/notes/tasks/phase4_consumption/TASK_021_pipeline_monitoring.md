# TASK_021: Pipeline Monitoring

## Description

Build pipeline monitoring capabilities using BigQuery metadata tables and Cloud Function logs. Track pipeline execution status, processing times, data volumes, and error rates.

## Prerequisites

- Phase 2 complete (pipeline running)
- TASK_013 complete (quality checks in place)

## Pipeline Run Tracking

### Create Pipeline Runs Table

```sql
CREATE TABLE IF NOT EXISTS `case_ficticio-data-mvp.case_ficticio_monitoring.pipeline_runs` (
  run_id STRING,
  run_date DATE,
  pipeline_stage STRING,      -- ingestion, silver_transform, gold_transform
  status STRING,              -- success, failure, partial
  records_processed INT64,
  records_rejected INT64,
  execution_time_seconds FLOAT64,
  error_message STRING,
  run_timestamp TIMESTAMP
);
```

### Log Pipeline Run from Cloud Function

Add to `cloud_functions/csv_processor/main.py`:

```python
import time

def log_pipeline_run(run_date, stage, status, processed, rejected, exec_time, error=None):
    """Log pipeline run to monitoring table."""
    client = bigquery.Client(project=PROJECT)
    table_id = f"{PROJECT}.case_ficticio_monitoring.pipeline_runs"

    rows = [{
        "run_id": str(uuid.uuid4()),
        "run_date": str(run_date),
        "pipeline_stage": stage,
        "status": status,
        "records_processed": processed,
        "records_rejected": rejected,
        "execution_time_seconds": exec_time,
        "error_message": error or "",
        "run_timestamp": datetime.utcnow().isoformat(),
    }]

    errors = client.insert_rows_json(table_id, rows)
    if errors:
        print(f"  [WARN] Failed to log pipeline run: {errors}")
```

### Daily Pipeline Health Query

```sql
-- Daily pipeline health summary
SELECT
  run_date,
  pipeline_stage,
  COUNT(*) AS total_runs,
  COUNTIF(status = 'success') AS successful,
  COUNTIF(status = 'failure') AS failed,
  SUM(records_processed) AS total_processed,
  SUM(records_rejected) AS total_rejected,
  ROUND(AVG(execution_time_seconds), 2) AS avg_execution_time_sec,
  ROUND(SAFE_DIVIDE(COUNTIF(status = 'success'), COUNT(*)) * 100, 1) AS success_rate_pct
FROM `case_ficticio-data-mvp.case_ficticio_monitoring.pipeline_runs`
WHERE run_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY run_date, pipeline_stage
ORDER BY run_date DESC, pipeline_stage;
```

### Unit Reporting Completeness

```sql
-- Which units reported data today?
SELECT
  u.unit_id,
  u.unit_name,
  CASE WHEN o.unit_id IS NOT NULL THEN 'REPORTED' ELSE 'MISSING' END AS status
FROM `case_ficticio-data-mvp.case_ficticio_silver.units` u
LEFT JOIN (
  SELECT DISTINCT unit_id
  FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`
  WHERE _ingest_date = CURRENT_DATE()
) o ON u.unit_id = o.unit_id
ORDER BY status DESC, u.unit_id;
```

## Acceptance Criteria

- [ ] pipeline_runs table created in monitoring dataset
- [ ] Cloud Function logs runs to pipeline_runs table
- [ ] Health summary query returns meaningful data
- [ ] Unit completeness check identifies missing units
- [ ] All monitoring queries execute within free tier

## Cost Impact

| Action | Cost |
|--------|------|
| Monitoring table storage (~1 MB) | Free |
| Monitoring queries (~50 MB/day) | Free |
| **Total** | **$0.00** |

---

*TASK_021 of 26 -- Phase 4: Consumption*
