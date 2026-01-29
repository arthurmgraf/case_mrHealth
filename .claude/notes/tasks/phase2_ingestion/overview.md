# Phase 2: Data Ingestion (Zero-Cost) -- Overview

## Summary

Phase 2 builds the data ingestion pipeline that moves data from source (CSV files and static reference data) into the Bronze layer of BigQuery. The original strategic plan used Dataproc (PySpark) and Datastream (PostgreSQL CDC), both of which incur costs. This MVP replaces them with Cloud Functions (Python/pandas) for CSV processing and a one-time static CSV export for reference data.

## Architecture Decision: Why Cloud Functions + pandas

| Criteria | Dataproc (PySpark) | Cloud Functions (pandas) | Decision |
|----------|-------------------|-------------------------|----------|
| Cost | ~$50/month | Free (2M invocations) | Cloud Functions |
| Complexity | High (Spark config) | Low (standard Python) | Cloud Functions |
| Data Volume | 100 CSVs x ~5 KB = 500 KB/day | Easily handled by pandas | Cloud Functions |
| Scalability | Excellent (distributed) | Sufficient for 50-200 units | Cloud Functions |
| Startup Time | 30-60s (cluster) | 1-3s (cold start) | Cloud Functions |

**Decision:** Cloud Functions with pandas. The daily data volume (~500 KB) does not justify Spark. When Case Fictício - Teste scales beyond 500 units, migration to Cloud Run or Dataproc becomes the upgrade path.

## Architecture Decision: PostgreSQL Reference Data

| Criteria | Datastream (CDC) | Static CSV Export | Decision |
|----------|-----------------|-------------------|----------|
| Cost | ~$10/month | Free | Static Export |
| Real-time sync | Yes | No (manual refresh) | Static Export (tables rarely change) |
| Complexity | PostgreSQL config + networking | Simple CSV upload | Static Export |

**Decision:** Static CSV export. Reference tables (products, units, states, countries) change infrequently. For MVP, a one-time export is sufficient. Document refresh procedure for future use.

## Objectives

1. Export and load static reference data (products, units, states, countries) into BigQuery
2. Create upload simulation script for unit CSV files to GCS
3. Deploy Cloud Function triggered by GCS file creation events
4. Implement CSV processing logic with pandas (schema enforcement, deduplication)
5. Load processed data into BigQuery Bronze layer (Parquet intermediate in GCS)
6. Implement data quality validation with quarantine for invalid records

## Tasks

| Task ID | Title | Priority | Estimated Time | Status |
|---------|-------|----------|----------------|--------|
| TASK_008 | Static Reference Data | HIGH | 1 hour | NOT STARTED |
| TASK_009 | CSV Upload Script | HIGH | 1 hour | NOT STARTED |
| TASK_010 | Cloud Function Trigger | HIGH | 2 hours | NOT STARTED |
| TASK_011 | CSV Processing Logic | HIGH | 3 hours | NOT STARTED |
| TASK_012 | Bronze Layer Loading | HIGH | 2 hours | NOT STARTED |
| TASK_013 | Data Quality Checks | MEDIUM | 2 hours | NOT STARTED |

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| Phase 1 | Upstream | GCP project, APIs, GCS bucket, BQ datasets, fake data |
| TASK_005 | Direct | Fake data must exist to test ingestion |
| TASK_003 | Direct | GCS bucket must exist |
| TASK_004 | Direct | BigQuery datasets must exist |
| Phase 3 | Downstream | Transformation requires Bronze layer populated |

## Free Tier Usage (Phase 2)

| Service | Free Tier Limit | Phase 2 Usage | Notes |
|---------|-----------------|---------------|-------|
| Cloud Functions | 2M invocations/month | ~1,500/month (50 units/day) | 99.9% headroom |
| Cloud Functions Compute | 400K GB-sec/month | ~5,000 GB-sec/month | 98.7% headroom |
| Cloud Storage | 5 GB | +100 MB (bronze Parquet) | 98% headroom |
| BigQuery Storage | 10 GB | +50 MB (bronze tables) | 99.5% headroom |
| BigQuery Queries | 1 TB/month | ~1 GB (load jobs) | 99.9% headroom |

## Data Flow

```
[Fake Data Generator] --> [output/csv_sales/] --> [upload_to_gcs.py] --> [GCS raw/csv_sales/]
                                                                              |
                                                                    [Eventarc Trigger]
                                                                              |
                                                                    [Cloud Function]
                                                                              |
                                                          [pandas: validate, clean, dedup]
                                                                    |              |
                                                              [Valid Data]    [Invalid Data]
                                                                    |              |
                                                           [GCS bronze/]    [GCS quarantine/]
                                                                    |
                                                           [BigQuery Bronze]

[Reference CSVs] --> [load_reference_data.py] --> [GCS raw/reference_data/] --> [BigQuery Bronze]
```

## Acceptance Criteria

- [ ] Reference data (4 tables) loaded into BigQuery Bronze
- [ ] Upload script successfully sends CSV files to GCS
- [ ] Cloud Function deploys and triggers on GCS file creation
- [ ] CSV processing correctly validates, cleans, and deduplicates data
- [ ] Valid data appears in BigQuery Bronze tables
- [ ] Invalid records quarantined with error reports
- [ ] All operations within free tier limits

---

*Phase 2 of 5 -- Case Fictício - Teste Data Platform MVP*
