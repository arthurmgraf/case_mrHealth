# TASK_006: IAM Service Accounts

## Description

Create service accounts with least-privilege IAM roles for the Case Fictício - Teste data platform. Separate service accounts are used for different pipeline stages to follow the principle of least privilege. All IAM operations are free.

## Prerequisites

- TASK_001 complete (GCP project exists)
- TASK_002 complete (IAM API enabled)

## Steps

### Step 1: Create Service Accounts

```bash
PROJECT="case_ficticio-data-mvp"

# Service account for Cloud Functions (ingestion pipeline)
gcloud iam service-accounts create sa-case_ficticio-ingestion \
  --project=$PROJECT \
  --display-name="MR Health Ingestion Pipeline" \
  --description="Service account for Cloud Functions that process CSV files"

# Service account for BigQuery transformations (scheduled queries)
gcloud iam service-accounts create sa-case_ficticio-transform \
  --project=$PROJECT \
  --display-name="MR Health Transformation Layer" \
  --description="Service account for BigQuery scheduled queries and transformations"

# Service account for monitoring and alerting
gcloud iam service-accounts create sa-case_ficticio-monitoring \
  --project=$PROJECT \
  --display-name="MR Health Monitoring" \
  --description="Service account for pipeline monitoring and alerting"
```

### Step 2: Assign IAM Roles

```bash
PROJECT="case_ficticio-data-mvp"

# --- Ingestion Service Account ---
SA_INGESTION="sa-case_ficticio-ingestion@${PROJECT}.iam.gserviceaccount.com"

# Read from GCS (landing zone)
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_INGESTION" \
  --role="roles/storage.objectViewer"

# Write to GCS (bronze layer, quarantine)
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_INGESTION" \
  --role="roles/storage.objectCreator"

# Load data into BigQuery bronze
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_INGESTION" \
  --role="roles/bigquery.dataEditor"

# Run BigQuery jobs
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_INGESTION" \
  --role="roles/bigquery.jobUser"

# --- Transformation Service Account ---
SA_TRANSFORM="sa-case_ficticio-transform@${PROJECT}.iam.gserviceaccount.com"

# Read/Write BigQuery data (all datasets)
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_TRANSFORM" \
  --role="roles/bigquery.dataEditor"

# Run BigQuery jobs
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_TRANSFORM" \
  --role="roles/bigquery.jobUser"

# --- Monitoring Service Account ---
SA_MONITORING="sa-case_ficticio-monitoring@${PROJECT}.iam.gserviceaccount.com"

# Read monitoring data
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_MONITORING" \
  --role="roles/monitoring.viewer"

# Read logs
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_MONITORING" \
  --role="roles/logging.viewer"

# Read BigQuery metadata (for monitoring queries)
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA_MONITORING" \
  --role="roles/bigquery.metadataViewer"
```

### Step 3: Create Key for Local Development (Optional)

```bash
# Only needed for local testing; Cloud Functions use attached SA
gcloud iam service-accounts keys create ./keys/sa-ingestion-key.json \
  --iam-account=$SA_INGESTION

# IMPORTANT: Add to .gitignore
echo "keys/" >> .gitignore
```

### Step 4: Verify Service Accounts

```bash
# List all service accounts
gcloud iam service-accounts list --project=$PROJECT

# Verify roles for ingestion SA
gcloud projects get-iam-policy $PROJECT \
  --flatten="bindings[].members" \
  --filter="bindings.members:sa-case_ficticio-ingestion" \
  --format="table(bindings.role)"
```

## IAM Role Matrix

| Service Account | Role | Purpose |
|----------------|------|---------|
| sa-case_ficticio-ingestion | storage.objectViewer | Read CSVs from raw/ |
| sa-case_ficticio-ingestion | storage.objectCreator | Write Parquet to bronze/ |
| sa-case_ficticio-ingestion | bigquery.dataEditor | Load data into bronze dataset |
| sa-case_ficticio-ingestion | bigquery.jobUser | Execute load jobs |
| sa-case_ficticio-transform | bigquery.dataEditor | Read/write silver, gold datasets |
| sa-case_ficticio-transform | bigquery.jobUser | Execute transformation queries |
| sa-case_ficticio-monitoring | monitoring.viewer | Read monitoring metrics |
| sa-case_ficticio-monitoring | logging.viewer | Read pipeline logs |
| sa-case_ficticio-monitoring | bigquery.metadataViewer | Read table metadata |

## Acceptance Criteria

- [ ] 3 service accounts created
- [ ] Each SA has appropriate roles (no over-permissioning)
- [ ] Verification commands confirm role assignments
- [ ] keys/ directory added to .gitignore (if local key created)

## Cost Impact

| Action | Cost |
|--------|------|
| Service account creation | Free |
| IAM role assignment | Free |
| **Total** | **$0.00** |

---

*TASK_006 of 26 -- Phase 1: Foundation*
