# Phase 1: Foundation -- Overview

## Summary

Phase 1 establishes the GCP infrastructure required for the Case Fictício - Teste data platform MVP. All resources are configured within the GCP Always Free Tier, ensuring zero monthly cost. The priority technical deliverable is the fake data generator script, which enables all subsequent phases to be tested with realistic data.

## Objectives

1. Create and configure GCP project with billing alerts at $0 threshold
2. Enable all required APIs for the data platform
3. Create GCS bucket with proper prefix structure for the medallion architecture
4. Create BigQuery datasets for Bronze, Silver, and Gold layers
5. **PRIORITY**: Build fake data generator script (`scripts/generate_fake_sales.py`)
6. Configure IAM service accounts with least-privilege access
7. Establish Git repository structure for all pipeline code

## Free Tier Services Used

| Service | Free Tier Limit | Phase 1 Usage |
|---------|-----------------|---------------|
| Cloud Storage | 5 GB Standard (US regions) | ~10 MB (test data) |
| BigQuery | 10 GB storage, 1 TB queries | ~50 MB storage |
| Cloud Functions | 2M invocations/month | 0 (setup only) |
| Cloud Scheduler | 3 jobs/month | 0 (setup only) |

## Tasks

| Task ID | Title | Priority | Estimated Time | Status |
|---------|-------|----------|----------------|--------|
| TASK_001 | GCP Project Setup | HIGH | 30 min | NOT STARTED |
| TASK_002 | Enable APIs | HIGH | 15 min | NOT STARTED |
| TASK_003 | GCS Bucket Setup | HIGH | 20 min | NOT STARTED |
| TASK_004 | BigQuery Datasets | HIGH | 20 min | NOT STARTED |
| TASK_005 | Fake Data Generator | CRITICAL | 2 hours | NOT STARTED |
| TASK_006 | IAM Service Accounts | MEDIUM | 30 min | NOT STARTED |
| TASK_007 | Repository Structure | MEDIUM | 30 min | NOT STARTED |

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| GCP Account | External | Must have a Google account with free tier eligibility |
| Python 3.9+ | External | Local development environment |
| gcloud CLI | External | Google Cloud SDK installed locally |
| None (upstream) | -- | This is the first phase; no upstream dependencies |
| Phase 2 (Ingestion) | Downstream | Requires all Phase 1 tasks complete |

## Acceptance Criteria

- [ ] GCP project created with billing alert at $0.01
- [ ] All required APIs enabled and verified
- [ ] GCS bucket exists with correct prefix structure
- [ ] BigQuery datasets (bronze, silver, gold) created
- [ ] Fake data generator produces valid ORDER.CSV and ORDER_ITEM.CSV
- [ ] Service account created with appropriate roles
- [ ] Git repository organized per the defined structure

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Free tier eligibility expired | HIGH | LOW | Verify eligibility before starting; check billing dashboard |
| Region restriction (US only for some free tier) | MEDIUM | MEDIUM | Use us-central1 for all resources |
| API quotas hit during testing | LOW | LOW | Monitor quotas; use conservative test data volumes |

---

*Phase 1 of 5 -- Case Fictício - Teste Data Platform MVP*
