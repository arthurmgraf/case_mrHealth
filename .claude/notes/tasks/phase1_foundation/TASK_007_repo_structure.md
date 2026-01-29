# TASK_007: Git Repository Structure

## Description

Organize the Git repository structure for the Case Fictício - Teste data platform MVP. The structure separates concerns: scripts (Python), SQL (BigQuery transformations), cloud functions, configuration, documentation, and tests.

## Prerequisites

- TASK_001 through TASK_006 complete (project context established)

## Steps

### Step 1: Create Repository Structure

```bash
# From project root
PROJECT_ROOT="."

# Scripts -- data generation and utilities
mkdir -p $PROJECT_ROOT/scripts

# Cloud Functions -- event-driven processing
mkdir -p $PROJECT_ROOT/cloud_functions/csv_processor

# SQL -- BigQuery transformations
mkdir -p $PROJECT_ROOT/sql/bronze
mkdir -p $PROJECT_ROOT/sql/silver
mkdir -p $PROJECT_ROOT/sql/gold
mkdir -p $PROJECT_ROOT/sql/monitoring
mkdir -p $PROJECT_ROOT/sql/scheduled_queries

# Tests
mkdir -p $PROJECT_ROOT/tests/unit
mkdir -p $PROJECT_ROOT/tests/integration
mkdir -p $PROJECT_ROOT/tests/sql

# Documentation
mkdir -p $PROJECT_ROOT/docs

# Configuration
mkdir -p $PROJECT_ROOT/config

# Keys (gitignored)
mkdir -p $PROJECT_ROOT/keys
```

### Step 2: Expected Structure

```
projeto_empresa_data_lakers/
|
|-- .claude/                          # Claude agent configuration (existing)
|   |-- notes/tasks/                  # Implementation task tracking
|
|-- scripts/
|   |-- generate_fake_sales.py        # Test data generator (TASK_005)
|   |-- upload_to_gcs.py              # Upload CSVs to GCS (TASK_009)
|   |-- load_reference_data.py        # Load static reference data (TASK_008)
|
|-- cloud_functions/
|   |-- csv_processor/
|   |   |-- main.py                   # Cloud Function entry point
|   |   |-- requirements.txt          # Python dependencies
|   |   |-- processing.py             # CSV processing logic
|   |   |-- quality.py                # Data quality checks
|
|-- sql/
|   |-- bronze/
|   |   |-- create_tables.sql         # Bronze table DDL
|   |-- silver/
|   |   |-- orders.sql                # Silver orders transformation
|   |   |-- order_items.sql           # Silver order items transformation
|   |   |-- reference_tables.sql      # Reference data cleaning
|   |-- gold/
|   |   |-- dim_date.sql              # Date dimension
|   |   |-- dim_product.sql           # Product dimension
|   |   |-- dim_unit.sql              # Unit dimension
|   |   |-- dim_geography.sql         # Geography dimension
|   |   |-- fact_sales.sql            # Sales fact table
|   |   |-- fact_order_items.sql      # Order items fact table
|   |-- monitoring/
|   |   |-- pipeline_runs.sql         # Pipeline run tracking
|   |   |-- quality_checks.sql        # Quality check results
|   |-- scheduled_queries/
|       |-- daily_silver_refresh.sql  # Daily silver layer refresh
|       |-- daily_gold_refresh.sql    # Daily gold layer refresh
|
|-- tests/
|   |-- unit/
|   |   |-- test_generate_fake_sales.py
|   |   |-- test_csv_processing.py
|   |-- integration/
|   |   |-- test_e2e_pipeline.py
|   |-- sql/
|       |-- test_silver_transforms.sql
|       |-- test_gold_models.sql
|
|-- docs/
|   |-- arquitetura_mvp_free_tier.md  # Zero-cost architecture document
|
|-- config/
|   |-- project_config.yaml           # Project-level configuration
|
|-- keys/                             # Service account keys (gitignored)
|
|-- case_CaseFicticio.md                  # Original case study
|-- strategic_implementation_plan.md  # Original strategic plan
|-- .gitignore
|-- requirements.txt                  # Python dependencies
```

### Step 3: Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Keys and secrets
keys/
*.json
!config/*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/
*.egg
.venv/
venv/
env/

# Generated data
output/
test_data/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
EOF
```

### Step 4: Create requirements.txt

```bash
cat > requirements.txt << 'EOF'
# Case Fictício - Teste Data Platform MVP -- Python Dependencies

# Data generation
faker>=22.0.0
pandas>=2.0.0

# GCP SDKs
google-cloud-storage>=2.14.0
google-cloud-bigquery>=3.17.0
google-cloud-functions-framework>=3.5.0

# Data processing
pyarrow>=14.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Code quality
ruff>=0.1.0
EOF
```

### Step 5: Create Project Configuration

```bash
cat > config/project_config.yaml << 'EOF'
# Case Fictício - Teste Data Platform MVP -- Project Configuration

project:
  id: case_ficticio-data-mvp
  name: MR Health Data Platform MVP
  region: us-central1
  environment: mvp

storage:
  bucket: case_ficticio-data-lake-mvp
  prefixes:
    raw_sales: raw/csv_sales
    raw_reference: raw/reference_data
    bronze: bronze
    quarantine: quarantine

bigquery:
  location: US
  datasets:
    bronze: case_ficticio_bronze
    silver: case_ficticio_silver
    gold: case_ficticio_gold
    monitoring: case_ficticio_monitoring

cloud_functions:
  csv_processor:
    name: csv-processor
    runtime: python311
    memory: 256MB
    timeout: 300s
    trigger_bucket: case_ficticio-data-lake-mvp
    trigger_prefix: raw/csv_sales/

cloud_scheduler:
  daily_pipeline:
    name: daily-transform-trigger
    schedule: "0 2 * * *"  # 2 AM daily
    timezone: America/Sao_Paulo

free_tier_limits:
  gcs_storage_gb: 5
  bq_storage_gb: 10
  bq_query_tb: 1
  functions_invocations: 2000000
  functions_gb_seconds: 400000
  scheduler_jobs: 3
EOF
```

## Acceptance Criteria

- [ ] All directories created
- [ ] .gitignore covers keys, venv, output, IDE files
- [ ] requirements.txt includes all needed Python packages
- [ ] config/project_config.yaml has all project settings
- [ ] Repository structure matches the defined layout

## Cost Impact

| Action | Cost |
|--------|------|
| Local file operations | Free |
| **Total** | **$0.00** |

---

*TASK_007 of 26 -- Phase 1: Foundation*
