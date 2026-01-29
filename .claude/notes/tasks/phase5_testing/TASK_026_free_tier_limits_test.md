# TASK_026: Free Tier Limits Test

## Description

Validate that all pipeline operations stay within GCP Free Tier limits even under realistic production load. This test estimates monthly usage across all services and provides a safety margin analysis.

## Prerequisites

- TASK_022 complete (cost monitoring queries available)
- E2E test run (TASK_025) completed at least once

## Free Tier Limits Assessment

### Test 1: BigQuery Query Volume Estimation

```sql
-- Calculate monthly query volume if pipeline runs daily
-- Use INFORMATION_SCHEMA to check actual usage

-- Actual bytes from today's operations
SELECT
  'Today actual usage' AS metric,
  ROUND(SUM(total_bytes_processed) / POW(1024, 3), 2) AS gb_today,
  ROUND(SUM(total_bytes_processed) / POW(1024, 3) * 30, 2) AS estimated_gb_monthly,
  ROUND(SUM(total_bytes_processed) / POW(1024, 3) * 30 / 1024, 4) AS estimated_tb_monthly,
  1.0 AS free_tier_tb,
  CASE
    WHEN SUM(total_bytes_processed) / POW(1024, 3) * 30 / 1024 < 0.5 THEN 'SAFE (< 50%)'
    WHEN SUM(total_bytes_processed) / POW(1024, 3) * 30 / 1024 < 0.8 THEN 'WARNING (50-80%)'
    ELSE 'CRITICAL (> 80%)'
  END AS status
FROM `region-us`.INFORMATION_SCHEMA.JOBS
WHERE creation_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE';
```

### Test 2: BigQuery Storage Projection

```sql
-- Project storage growth over 12 months
WITH monthly_growth AS (
  SELECT
    ROUND(SUM(size_bytes) / POW(1024, 3), 4) AS current_gb
  FROM `case_ficticio-data-mvp`.`region-us`.INFORMATION_SCHEMA.TABLE_STORAGE
)
SELECT
  current_gb,
  ROUND(current_gb * 12, 2) AS projected_12mo_gb,
  10.0 AS free_tier_gb,
  CASE
    WHEN current_gb * 12 < 5 THEN 'SAFE (< 50%)'
    WHEN current_gb * 12 < 8 THEN 'WARNING (50-80%)'
    ELSE 'CRITICAL (> 80%)'
  END AS status,
  ROUND((10.0 - current_gb) / current_gb, 0) AS months_until_limit
FROM monthly_growth;
```

### Test 3: Cloud Functions Usage Estimation

| Metric | Daily | Monthly | Free Tier | % Used |
|--------|-------|---------|-----------|--------|
| Invocations | ~100 (50 units x 2 files) | ~3,000 | 2,000,000 | 0.15% |
| Compute (GB-sec) | ~200 (2s x 100 x 256MB) | ~6,000 | 400,000 | 1.5% |
| Networking (GB) | ~0.001 | ~0.03 | 5 GB egress | 0.6% |

### Test 4: Cloud Storage Usage Estimation

| Prefix | Daily Growth | Monthly Growth | 12-Month Projection |
|--------|-------------|----------------|---------------------|
| raw/csv_sales | ~500 KB | ~15 MB | ~180 MB |
| raw/reference_data | 0 (static) | 0 | ~10 KB |
| bronze/ | ~300 KB | ~9 MB | ~108 MB |
| quarantine/ | ~50 KB | ~1.5 MB | ~18 MB |
| **Total** | **~850 KB** | **~25 MB** | **~306 MB** |
| **Free Tier** | | | **5,120 MB (5 GB)** |
| **Usage %** | | | **~6%** |

### Test 5: Cloud Scheduler Verification

```
MVP uses 3 scheduled jobs (the free tier maximum):
1. daily-silver-refresh (2:00 AM)
2. daily-gold-refresh (2:15 AM)
3. daily-quality-check (2:30 AM)

Status: AT LIMIT (3/3)
Mitigation: Combine jobs if additional schedule needed
```

### Test 6: Worst Case Scenario

Calculate usage if all 50 units send maximum data for 30 days:

| Service | Worst Case Monthly | Free Tier | Safe? |
|---------|-------------------|-----------|-------|
| GCS Storage | 50 MB new/month + 306 MB cumulative | 5 GB | YES (16 months to limit) |
| BQ Storage | 120 MB active | 10 GB | YES (83x headroom) |
| BQ Queries | ~60 GB/month | 1,024 GB | YES (17x headroom) |
| CF Invocations | 3,000/month | 2,000,000 | YES (667x headroom) |
| CF Compute | 6,000 GB-sec | 400,000 | YES (67x headroom) |

## Scaling Thresholds (When to Move Beyond Free Tier)

| Metric | Free Tier Limit | Upgrade Trigger | Expected Timeline |
|--------|-----------------|-----------------|-------------------|
| Units | - | 200+ units | 12-18 months |
| GCS Storage | 5 GB | > 4 GB | 16+ months |
| BQ Storage | 10 GB | > 8 GB | 24+ months |
| BQ Queries | 1 TB/month | > 800 GB/month | Unlikely for MVP |
| CF Invocations | 2M/month | > 1.5M/month | 200+ units |

## Acceptance Criteria

- [ ] All free tier usage estimates show SAFE status (< 50%)
- [ ] 12-month projection stays within limits
- [ ] Worst-case scenario still within limits
- [ ] Cloud Scheduler at limit (3/3) documented with mitigation
- [ ] Upgrade thresholds clearly defined

## Cost Impact

| Action | Cost |
|--------|------|
| Assessment queries (INFORMATION_SCHEMA) | Free |
| **Total** | **$0.00** |

---

*TASK_026 of 26 -- Phase 5: Testing*
