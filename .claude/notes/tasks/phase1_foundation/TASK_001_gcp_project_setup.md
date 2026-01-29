# TASK_001: GCP Project Setup

## Description

Create a new GCP project configured for the Case Fictício - Teste data platform MVP. The project must be linked to a billing account (required even for free tier) with billing alerts set to trigger at $0.01 to prevent any accidental charges.

## Prerequisites

- Google account with GCP free tier eligibility
- Google Cloud SDK (gcloud CLI) installed locally
- Web browser access to console.cloud.google.com

## Steps

### Step 1: Create GCP Project

```bash
# Set project variables
export PROJECT_ID="case_ficticio-data-mvp"
export PROJECT_NAME="MR Health Data MVP"
export BILLING_ACCOUNT_ID="your-billing-account-id"

# Create the project
gcloud projects create $PROJECT_ID \
  --name="$PROJECT_NAME" \
  --labels=environment=mvp,cost=free-tier

# Set as active project
gcloud config set project $PROJECT_ID
```

### Step 2: Link Billing Account

```bash
# Link billing account (required even for free tier)
gcloud billing projects link $PROJECT_ID \
  --billing-account=$BILLING_ACCOUNT_ID
```

### Step 3: Set Default Region (US for free tier)

```bash
# Set default region -- MUST be US for free tier eligibility
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

### Step 4: Create Budget Alert at $0.01

This must be done via the Console UI or via the API:

```bash
# Via gcloud (budget API)
# First, enable the billing budget API
gcloud services enable billingbudgets.googleapis.com

# Create a budget alert -- set to $1 to catch any charges
# Note: The minimum budget via API is $1; set email alerts at 1% ($0.01)
cat > /tmp/budget.json << 'EOF'
{
  "displayName": "MR Health Zero-Cost Alert",
  "budgetFilter": {
    "projects": ["projects/case_ficticio-data-mvp"]
  },
  "amount": {
    "specifiedAmount": {
      "currencyCode": "USD",
      "units": "1"
    }
  },
  "thresholdRules": [
    {
      "thresholdPercent": 0.01,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.5,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 1.0,
      "spendBasis": "CURRENT_SPEND"
    }
  ],
  "notificationsRule": {
    "schemaVersion": "1.0",
    "disableDefaultIamRecipients": false
  }
}
EOF
```

**Alternative (Console UI -- Recommended):**
1. Go to https://console.cloud.google.com/billing
2. Select billing account
3. Click "Budgets & alerts"
4. Create budget: Name = "MR Health Zero Cost", Amount = $1
5. Set alert thresholds at 1%, 50%, 100%
6. Enable email notifications

### Step 5: Verify Setup

```bash
# Verify project is active
gcloud config list project

# Verify billing is linked
gcloud billing projects describe $PROJECT_ID

# Verify region
gcloud config list compute/region
```

## Acceptance Criteria

- [ ] Project `case_ficticio-data-mvp` exists and is active
- [ ] Billing account linked (required for API access)
- [ ] Budget alert configured to notify at $0.01 spend
- [ ] Default region set to `us-central1`
- [ ] `gcloud config list` shows correct project and region

## Verification Commands

```bash
# Should return the project ID
gcloud config get-value project
# Expected: case_ficticio-data-mvp

# Should show billing enabled
gcloud billing projects describe case_ficticio-data-mvp --format="value(billingEnabled)"
# Expected: True

# Should show us-central1
gcloud config get-value compute/region
# Expected: us-central1
```

## Cost Impact

| Action | Cost |
|--------|------|
| Project creation | Free |
| Billing account link | Free |
| Budget alert | Free |
| **Total** | **$0.00** |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Project ID already exists" | Choose a different project ID (add random suffix) |
| "Billing account not found" | Run `gcloud billing accounts list` to find your account |
| "Free trial expired" | Free tier != Free trial. Free tier is always free even after trial expires |

---

*TASK_001 of 26 -- Phase 1: Foundation*
