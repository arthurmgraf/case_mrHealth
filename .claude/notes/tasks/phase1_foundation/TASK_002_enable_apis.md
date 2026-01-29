# TASK_002: Enable Required APIs

## Description

Enable all GCP APIs required for the Case Fictício - Teste data platform MVP. Only free-tier-compatible APIs are enabled. No paid-only services (Dataproc, Datastream, Cloud Workflows) are included.

## Prerequisites

- TASK_001 complete (GCP project created and active)

## Steps

### Step 1: Enable Core APIs

```bash
# Set project
gcloud config set project case_ficticio-data-mvp

# Enable APIs in batch
gcloud services enable \
  storage.googleapis.com \
  bigquery.googleapis.com \
  bigquerydatatransfer.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  eventarc.googleapis.com \
  run.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### Step 2: API Purpose Reference

| API | Service | Purpose in MVP | Free Tier |
|-----|---------|----------------|-----------|
| `storage.googleapis.com` | Cloud Storage | Data lake (raw/bronze CSVs and Parquet) | 5 GB Standard (US) |
| `bigquery.googleapis.com` | BigQuery | Silver/Gold analytics warehouse | 10 GB storage, 1 TB queries |
| `bigquerydatatransfer.googleapis.com` | BQ Data Transfer | Scheduled queries (free) | Free for scheduled queries |
| `cloudfunctions.googleapis.com` | Cloud Functions | Event-driven CSV processing | 2M invocations/month |
| `cloudbuild.googleapis.com` | Cloud Build | Deploy Cloud Functions | 120 build-min/day free |
| `cloudscheduler.googleapis.com` | Cloud Scheduler | Trigger daily pipeline | 3 jobs/month free |
| `eventarc.googleapis.com` | Eventarc | GCS event triggers for Functions | Free (event routing) |
| `run.googleapis.com` | Cloud Run | Cloud Functions 2nd gen runtime | 2M requests/month |
| `monitoring.googleapis.com` | Cloud Monitoring | Pipeline and cost monitoring | Free tier generous |
| `logging.googleapis.com` | Cloud Logging | Pipeline logging | 50 GB/month free |
| `iam.googleapis.com` | IAM | Service account management | Free |
| `cloudresourcemanager.googleapis.com` | Resource Manager | Project management | Free |

### Step 3: Verify All APIs Enabled

```bash
# List all enabled APIs
gcloud services list --enabled --format="table(config.name,config.title)"

# Verify specific critical APIs
for api in storage bigquery cloudfunctions cloudscheduler; do
  echo -n "$api: "
  gcloud services list --enabled --filter="config.name:$api" --format="value(config.name)" | head -1
done
```

## APIs Explicitly NOT Enabled (Cost Avoidance)

| API | Service | Why Not |
|-----|---------|---------|
| `dataproc.googleapis.com` | Dataproc | $0.01/vCPU-hour minimum; replaced by Cloud Functions |
| `datastream.googleapis.com` | Datastream | $0.10/GB; replaced by static CSV export |
| `workflows.googleapis.com` | Cloud Workflows | Limited free tier; replaced by Cloud Scheduler + Functions |
| `composer.googleapis.com` | Cloud Composer | ~$300/month minimum; replaced by Cloud Scheduler |

## Acceptance Criteria

- [ ] All 12 APIs from Step 1 are enabled
- [ ] Verification command shows all expected APIs
- [ ] No paid-only APIs (Dataproc, Datastream, Workflows, Composer) are enabled

## Verification Commands

```bash
# Count enabled APIs (should be >= 12)
gcloud services list --enabled --format="value(config.name)" | wc -l

# Verify no paid services accidentally enabled
gcloud services list --enabled --filter="config.name:(dataproc OR datastream OR workflows OR composer)" --format="value(config.name)"
# Expected: empty output
```

## Cost Impact

| Action | Cost |
|--------|------|
| Enabling APIs | Free |
| API at rest (no usage) | Free |
| **Total** | **$0.00** |

---

*TASK_002 of 26 -- Phase 1: Foundation*
