# TASK_003: GCS Bucket Setup

## Description

Create a single Cloud Storage bucket with a prefix-based structure to support the medallion architecture (raw/bronze layers). A single bucket is used instead of multiple buckets to simplify management and stay well within the 5 GB free tier limit. The Gold/Silver layers live in BigQuery, not GCS.

## Prerequisites

- TASK_001 complete (GCP project exists)
- TASK_002 complete (Storage API enabled)

## Steps

### Step 1: Create the Bucket

```bash
# IMPORTANT: Must be us-central1, us-east1, or us-west1 for free tier
export BUCKET_NAME="case_ficticio-data-lake-mvp"
export REGION="us-central1"

gsutil mb \
  -p case_ficticio-data-mvp \
  -c STANDARD \
  -l $REGION \
  -b on \
  gs://$BUCKET_NAME/
```

**Note:** Uniform bucket-level access (`-b on`) is recommended for security.

### Step 2: Create Prefix Structure

```bash
# Create placeholder objects to establish prefix structure
# (GCS uses flat namespace; prefixes are virtual directories)

BUCKET="gs://case_ficticio-data-lake-mvp"

# RAW layer -- landing zone for unit CSVs
gsutil cp /dev/null ${BUCKET}/raw/csv_sales/.keep
gsutil cp /dev/null ${BUCKET}/raw/reference_data/.keep

# BRONZE layer -- processed Parquet files
gsutil cp /dev/null ${BUCKET}/bronze/orders/.keep
gsutil cp /dev/null ${BUCKET}/bronze/order_items/.keep
gsutil cp /dev/null ${BUCKET}/bronze/products/.keep
gsutil cp /dev/null ${BUCKET}/bronze/units/.keep
gsutil cp /dev/null ${BUCKET}/bronze/states/.keep
gsutil cp /dev/null ${BUCKET}/bronze/countries/.keep

# QUARANTINE -- files with validation errors
gsutil cp /dev/null ${BUCKET}/quarantine/.keep

# SCRIPTS -- Cloud Function source, utility scripts
gsutil cp /dev/null ${BUCKET}/scripts/.keep
```

### Step 3: Expected Prefix Structure

```
gs://case_ficticio-data-lake-mvp/
|
+-- raw/
|   +-- csv_sales/
|   |   +-- {YYYY}/{MM}/{DD}/
|   |       +-- unit_{NNN}/
|   |           +-- pedido.csv
|   |           +-- item_pedido.csv
|   |
|   +-- reference_data/
|       +-- produto.csv
|       +-- unidade.csv
|       +-- estado.csv
|       +-- pais.csv
|
+-- bronze/
|   +-- orders/
|   |   +-- ingest_date={YYYY-MM-DD}/
|   |       +-- orders.parquet
|   |
|   +-- order_items/
|   |   +-- ingest_date={YYYY-MM-DD}/
|   |       +-- order_items.parquet
|   |
|   +-- products/
|   +-- units/
|   +-- states/
|   +-- countries/
|
+-- quarantine/
|   +-- {YYYY}/{MM}/{DD}/
|       +-- unit_{NNN}/
|           +-- pedido.csv
|           +-- _error_report.json
|
+-- scripts/
```

### Step 4: Set Lifecycle Rules (Optional for MVP)

```bash
# For MVP, no lifecycle rules needed (data is small)
# For future: move old raw data to Nearline after 30 days
# This saves cost only AFTER exceeding free tier (5 GB)

cat > /tmp/lifecycle.json << 'EOF'
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {
        "age": 30,
        "matchesPrefix": ["raw/"]
      }
    }
  ]
}
EOF

# Apply lifecycle (optional -- not needed for MVP free tier usage)
# gsutil lifecycle set /tmp/lifecycle.json gs://case_ficticio-data-lake-mvp/
```

### Step 5: Verify Bucket

```bash
# Check bucket exists
gsutil ls gs://case_ficticio-data-lake-mvp/

# Check bucket metadata
gsutil ls -L -b gs://case_ficticio-data-lake-mvp/ | head -20

# Verify region is US
gsutil ls -L -b gs://case_ficticio-data-lake-mvp/ | grep "Location"
# Expected: Location constraint: US-CENTRAL1

# Verify storage class
gsutil ls -L -b gs://case_ficticio-data-lake-mvp/ | grep "Storage class"
# Expected: Storage class: STANDARD

# List prefix structure
gsutil ls gs://case_ficticio-data-lake-mvp/
# Expected:
# gs://case_ficticio-data-lake-mvp/bronze/
# gs://case_ficticio-data-lake-mvp/quarantine/
# gs://case_ficticio-data-lake-mvp/raw/
# gs://case_ficticio-data-lake-mvp/scripts/
```

## Storage Budget Calculation

| Layer | Content | Estimated Size | Retention |
|-------|---------|----------------|-----------|
| raw/csv_sales | 100 CSV files/day x ~5 KB each | ~500 KB/day = ~15 MB/month | Permanent |
| raw/reference_data | 4 static CSV files | ~10 KB total | Permanent |
| bronze/ | Parquet files (compressed) | ~300 KB/day = ~9 MB/month | 2 months |
| quarantine/ | Error files (rare) | ~1 MB/month | 1 month |
| **Total (Month 1)** | | **~25 MB** | |
| **Total (Month 12)** | | **~200 MB** | Well within 5 GB |

## Acceptance Criteria

- [ ] Bucket `case_ficticio-data-lake-mvp` exists in `us-central1`
- [ ] Storage class is STANDARD
- [ ] Uniform bucket-level access is ON
- [ ] Prefix structure (raw/, bronze/, quarantine/, scripts/) verified
- [ ] Storage estimate confirms we stay within 5 GB free tier

## Cost Impact

| Action | Cost |
|--------|------|
| Bucket creation | Free |
| Storage (< 5 GB, US, Standard) | Free |
| **Total** | **$0.00** |

---

*TASK_003 of 26 -- Phase 1: Foundation*
