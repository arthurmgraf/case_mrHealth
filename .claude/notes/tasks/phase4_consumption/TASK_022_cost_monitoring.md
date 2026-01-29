# TASK_022: Free Tier Cost Monitoring

## Description

Create monitoring queries and a dashboard to track GCP free tier usage. This is critical to prevent accidental charges. Track BigQuery query volume, Cloud Storage usage, Cloud Functions invocations, and overall billing.

## Prerequisites

- TASK_001 complete (billing alerts configured)
- All previous phases contributing to usage

## Steps

### Step 1: BigQuery Query Usage Monitoring

```sql
-- Monthly BigQuery query bytes processed
-- Free tier: 1 TB/month
SELECT
  DATE_TRUNC(creation_time, MONTH) AS month,
  COUNT(*) AS total_queries,
  ROUND(SUM(total_bytes_processed) / POW(1024, 3), 2) AS gb_processed,
  ROUND(SUM(total_bytes_processed) / POW(1024, 4), 4) AS tb_processed,
  ROUND(SUM(total_bytes_processed) / POW(1024, 4) / 1.0 * 100, 2) AS pct_of_free_tier,
  CASE
    WHEN SUM(total_bytes_processed) / POW(1024, 4) < 0.5 THEN 'SAFE'
    WHEN SUM(total_bytes_processed) / POW(1024, 4) < 0.8 THEN 'WARNING'
    ELSE 'CRITICAL'
  END AS status
FROM `region-us`.INFORMATION_SCHEMA.JOBS
WHERE creation_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
  AND job_type = 'QUERY'
  AND state = 'DONE'
GROUP BY month;
```

### Step 2: BigQuery Storage Usage Monitoring

```sql
-- BigQuery storage usage per dataset
-- Free tier: 10 GB active storage
SELECT
  table_schema AS dataset,
  COUNT(*) AS table_count,
  ROUND(SUM(size_bytes) / POW(1024, 2), 2) AS size_mb,
  ROUND(SUM(size_bytes) / POW(1024, 3), 4) AS size_gb,
  ROUND(SUM(size_bytes) / POW(1024, 3) / 10.0 * 100, 2) AS pct_of_free_tier
FROM `case_ficticio-data-mvp`.`region-us`.INFORMATION_SCHEMA.TABLE_STORAGE
GROUP BY dataset
ORDER BY size_mb DESC;

-- Total storage
SELECT
  ROUND(SUM(size_bytes) / POW(1024, 3), 4) AS total_gb,
  10.0 AS free_tier_gb,
  ROUND(SUM(size_bytes) / POW(1024, 3) / 10.0 * 100, 2) AS pct_used,
  CASE
    WHEN SUM(size_bytes) / POW(1024, 3) < 5 THEN 'SAFE'
    WHEN SUM(size_bytes) / POW(1024, 3) < 8 THEN 'WARNING'
    ELSE 'CRITICAL'
  END AS status
FROM `case_ficticio-data-mvp`.`region-us`.INFORMATION_SCHEMA.TABLE_STORAGE;
```

### Step 3: GCS Storage Monitoring

```bash
# Check total GCS usage
gsutil du -s gs://case_ficticio-data-lake-mvp/
# Compare against 5 GB free tier

# Breakdown by prefix
gsutil du -s gs://case_ficticio-data-lake-mvp/raw/
gsutil du -s gs://case_ficticio-data-lake-mvp/bronze/
gsutil du -s gs://case_ficticio-data-lake-mvp/quarantine/
```

### Step 4: Cloud Functions Invocation Monitoring

```bash
# Monthly invocations count
gcloud functions logs read csv-processor --gen2 --region=us-central1 \
  --start-time=$(date -u -d "$(date +%Y-%m-01)" +%Y-%m-%dT%H:%M:%SZ) \
  --format="value(LOG)" | wc -l
```

BigQuery monitoring query for function metrics:

```sql
-- Cloud Function invocations from Cloud Logging
-- (Requires log sink to BigQuery, or use Cloud Monitoring API)
-- Simpler approach: count pipeline_runs as proxy
SELECT
  DATE_TRUNC(run_timestamp, MONTH) AS month,
  COUNT(*) AS invocations,
  2000000 AS free_tier_limit,
  ROUND(COUNT(*) / 2000000.0 * 100, 4) AS pct_used
FROM `case_ficticio-data-mvp.case_ficticio_monitoring.pipeline_runs`
WHERE pipeline_stage = 'ingestion'
GROUP BY month;
```

### Step 5: Free Tier Dashboard Summary Query

```sql
-- Comprehensive free tier usage dashboard
-- Run this weekly to monitor all services

SELECT 'BigQuery Queries' AS service,
  ROUND(SUM(total_bytes_processed) / POW(1024, 4), 4) AS used,
  1.0 AS free_limit,
  'TB' AS unit,
  ROUND(SUM(total_bytes_processed) / POW(1024, 4) / 1.0 * 100, 2) AS pct_used
FROM `region-us`.INFORMATION_SCHEMA.JOBS
WHERE creation_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
  AND job_type = 'QUERY' AND state = 'DONE'

UNION ALL

SELECT 'BigQuery Storage',
  ROUND(SUM(size_bytes) / POW(1024, 3), 4),
  10.0, 'GB',
  ROUND(SUM(size_bytes) / POW(1024, 3) / 10.0 * 100, 2)
FROM `case_ficticio-data-mvp`.`region-us`.INFORMATION_SCHEMA.TABLE_STORAGE

UNION ALL

SELECT 'Cloud Functions',
  CAST(COUNT(*) AS FLOAT64),
  2000000.0, 'invocations',
  ROUND(COUNT(*) / 2000000.0 * 100, 4)
FROM `case_ficticio-data-mvp.case_ficticio_monitoring.pipeline_runs`
WHERE pipeline_stage = 'ingestion'
  AND EXTRACT(MONTH FROM run_timestamp) = EXTRACT(MONTH FROM CURRENT_TIMESTAMP());
```

## Free Tier Limits Reference Card

```
+----------------------------+------------------+-----------+
| Service                    | Free Tier Limit  | Alert At  |
+----------------------------+------------------+-----------+
| GCS Storage                | 5 GB Standard    | 4 GB (80%)|
| BigQuery Storage           | 10 GB Active     | 8 GB (80%)|
| BigQuery Queries           | 1 TB / month     | 800 GB    |
| Cloud Functions Invocations| 2M / month       | 1.6M (80%)|
| Cloud Functions Compute    | 400K GB-sec/mo   | 320K (80%)|
| Cloud Scheduler            | 3 jobs           | At limit  |
| Cloud Logging              | 50 GB / month    | 40 GB     |
+----------------------------+------------------+-----------+
```

## Acceptance Criteria

- [ ] BigQuery query usage query returns current month stats
- [ ] BigQuery storage query shows dataset breakdown
- [ ] Free tier summary query shows all services in one view
- [ ] All monitoring queries themselves use minimal bytes
- [ ] GCS monitoring commands work

## Cost Impact

| Action | Cost |
|--------|------|
| INFORMATION_SCHEMA queries | Free (metadata queries are free) |
| Monitoring overhead | Negligible |
| **Total** | **$0.00** |

---

*TASK_022 of 26 -- Phase 4: Consumption*
