# TASK_020: Monitoring and Alerting (Free Tier)

## Description

Set up Cloud Monitoring alerts for pipeline health and cost monitoring. Cloud Monitoring has a generous free tier. Alerts notify via email when the pipeline fails, data is stale, or free tier usage approaches limits.

## Prerequisites

- TASK_002 complete (Monitoring API enabled)
- Phase 2 complete (pipeline running to generate metrics)

## Steps

### Step 1: Create Notification Channel (Email)

```bash
# Create an email notification channel
gcloud beta monitoring channels create \
  --display-name="MR Health Alerts" \
  --type=email \
  --channel-labels=email_address=your-email@example.com
```

### Step 2: Alert -- Cloud Function Errors

```bash
# Alert when Cloud Function has execution errors
gcloud beta monitoring policies create \
  --display-name="CSV Processor Errors" \
  --condition-display-name="Function execution errors > 0" \
  --condition-filter='resource.type="cloud_function" AND metric.type="cloudfunctions.googleapis.com/function/execution_count" AND metric.labels.status!="ok"' \
  --condition-threshold-value=1 \
  --condition-threshold-duration=300s \
  --condition-threshold-comparison=COMPARISON_GT \
  --notification-channels=<channel-id>
```

### Step 3: Alert -- Data Freshness

Create a custom metric check using a scheduled BigQuery query:

```sql
-- Run as scheduled query at 8:00 AM daily
-- Check if data was ingested today
SELECT
  CASE
    WHEN MAX(_ingest_date) < CURRENT_DATE()
    THEN ERROR(CONCAT('Data freshness alert: last ingestion was ', CAST(MAX(_ingest_date) AS STRING)))
    ELSE 'OK'
  END as freshness_check
FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`;
```

### Step 4: Alert -- BigQuery Query Usage

Monitor query bytes processed to stay within 1 TB/month:

```sql
-- Monthly query usage check (run weekly)
SELECT
  SUM(total_bytes_processed) / (1024*1024*1024*1024) AS tb_processed,
  1.0 AS tb_limit,
  ROUND(SUM(total_bytes_processed) / (1024*1024*1024*1024) / 1.0 * 100, 2) AS pct_used
FROM `region-us`.INFORMATION_SCHEMA.JOBS
WHERE creation_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
  AND job_type = 'QUERY'
  AND state = 'DONE';
```

### Step 5: Log-Based Metrics

```bash
# Create a log-based metric for function errors
gcloud logging metrics create csv_processor_errors \
  --description="Count of CSV processor Cloud Function errors" \
  --log-filter='resource.type="cloud_function" AND resource.labels.function_name="csv-processor" AND severity>=ERROR'

# Create a log-based metric for successful processing
gcloud logging metrics create csv_processor_success \
  --description="Count of successful CSV processing events" \
  --log-filter='resource.type="cloud_function" AND resource.labels.function_name="csv-processor" AND textPayload=~"Loaded .* rows"'
```

## Alert Summary

| Alert | Trigger | Channel | Severity |
|-------|---------|---------|----------|
| Function Errors | Error count > 0 in 5 min | Email | CRITICAL |
| Data Freshness | No ingestion by 8 AM | Email | HIGH |
| Query Usage > 80% | > 800 GB/month | Email | WARNING |
| Storage Usage > 80% | > 8 GB active | Email | WARNING |

## Acceptance Criteria

- [ ] Email notification channel created
- [ ] Cloud Function error alert configured
- [ ] Data freshness check scheduled
- [ ] Query usage monitoring query works
- [ ] Log-based metrics created for function success/error

## Cost Impact

| Action | Cost |
|--------|------|
| Cloud Monitoring (free tier) | Free |
| Alert notifications (email) | Free |
| Log-based metrics | Free (within 50 GB/month logging) |
| **Total** | **$0.00** |

---

*TASK_020 of 26 -- Phase 4: Consumption*
