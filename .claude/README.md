# Do Zero a Producao - Claude Code

> Data platform for MR. Health restaurant chain with event-driven CSV ingestion, BigQuery medallion architecture, and Claude Code agentic development.

---

## Overview

### What This Is

This project is a production-ready data platform for the MR. Health restaurant chain, built using Claude Code as the primary development environment. It implements event-driven CSV sales data ingestion into a BigQuery medallion architecture (Bronze/Silver/Gold), with automated data generation for testing and a comprehensive SQL transformation layer.

The project also showcases agentic development practices with 40+ specialized Claude Code agents and a 7-domain knowledge base used throughout the development lifecycle.

### Why This Exists

MR. Health operates 50 restaurant units across Southern Brazil (RS, SC, PR). This platform automates sales data ingestion and transformation, replacing manual data consolidation with an event-driven pipeline that processes CSV sales files automatically upon upload to GCS.

This project also serves as a reference implementation for:

- **Agentic Development:** Leveraging Claude Code's custom agent system for domain-specific development tasks
- **Cloud-Native Architecture:** Event-driven serverless pipeline on GCP
- **Data Modeling:** BigQuery medallion architecture with star schema in the Gold layer

### Who This Is For

- **Data Engineers** building event-driven data pipelines on GCP
- **Platform Engineers** implementing serverless architectures with Cloud Functions
- **Teams** exploring agentic development workflows with Claude Code

---

## Quick Start

### Prerequisites

- Claude Code CLI installed and configured
- Google Cloud Platform account with billing enabled
- Python 3.11+
- gcloud CLI authenticated

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/btc-zero-prd-claude-code.git
cd btc-zero-prd-claude-code

# Install dependencies
pip install -r requirements.txt

# Configure GCP project
gcloud config set project <your-project-id>

# Deploy infrastructure (BigQuery datasets and tables)
python scripts/deploy_phase1_infrastructure.py

# Generate fake sales data
python scripts/generate_fake_sales.py

# Upload data to GCS
python scripts/upload_fake_data_to_gcs.py
```

### Using Custom Agents

This project includes 40+ specialized agents for Claude Code development:

```bash
# Architecture and planning
> /agent the-planner          # Strategic planning and roadmaps
> /agent pipeline-architect   # Data pipeline design

# Implementation
> /agent function-developer    # Cloud Function development
> /agent python-developer      # Python code patterns

# Quality and review
> /agent code-reviewer        # Security and quality review
> /agent test-generator       # Automated test creation
```

---

## Features

### Event-Driven CSV Ingestion

- **Cloud Function (2nd Gen)** triggered by GCS file uploads via Eventarc
- **CSV validation** with schema checking and deduplication
- **Quarantine system** for invalid files with error reports
- **GCS buckets** for raw data landing zone and quarantine

### BigQuery Medallion Architecture

- **Bronze layer:** Raw ingested data with metadata (`_ingest_date`, `_source_file`)
- **Silver layer:** Cleaned and normalized data with joins and deduplication
- **Gold layer:** Star schema with dimension and fact tables, plus KPI aggregations

### Data Generation and Testing

- **Fake data generator** with realistic distributions across 50 units, 30 products, 30 days
- **Reproducible runs** with seed support for deterministic output
- **Unit tests** with 97.2% coverage on data generation logic

### Claude Code Agent Ecosystem

- **40+ specialized agents** for every development task
- **7 knowledge base domains** with validated patterns
- **MCP integration** for real-time technology validation

---

## Architecture

### Pipeline Architecture

```text
                    MR. HEALTH DATA PLATFORM - PIPELINE ARCHITECTURE
+---------------------------------------------------------------------------------+
|                                                                                 |
|  INGESTION                    TRANSFORMATION                   CONSUMPTION      |
|  ---------                    --------------                   -----------      |
|                                                                                 |
|  +----------+   +-----------+   +---------+   +---------+   +------------+     |
|  | CSV Files|-->| Cloud     |-->| Bronze  |-->| Silver  |-->|   Gold     |     |
|  | (GCS)    |   | Function  |   | (BQ)    |   | (BQ)    |   |  (BQ)      |     |
|  +----------+   +-----------+   +---------+   +---------+   +------------+     |
|       |              |                                            |             |
|   Eventarc       Validates &                                 Star Schema       |
|   trigger        loads to BQ                              + Aggregations       |
|                                                                                 |
|  -------------------------------------------------------------------------     |
|                                                                                 |
|  DATA MODEL (Gold Layer - Star Schema)                                         |
|  -------------------------------------                                         |
|                                                                                 |
|  Dimensions:                        Facts:              Aggregations:           |
|  +------------+                     +------------+      +-------------------+   |
|  | dim_date   |                     | fact_sales |      | agg_daily_sales   |   |
|  | dim_product|                     | fact_order |      | agg_unit_perf     |   |
|  | dim_unit   |                     |   _items   |      | agg_product_perf  |   |
|  | dim_geo    |                     +------------+      +-------------------+   |
|  +------------+                                                                 |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

### Project Structure

```text
projeto_empresa_data_lakers/
+-- cloud_functions/
|   +-- csv_processor/          # Cloud Function for CSV ingestion
|       +-- main.py             # Entry point (Eventarc GCS trigger)
|       +-- requirements.txt
|       +-- deploy.ps1
+-- scripts/
|   +-- generate_fake_sales.py  # Fake data generator (50 units, 30 days)
|   +-- deploy_phase1_infrastructure.py  # BigQuery setup via Python SDK
|   +-- upload_fake_data_to_gcs.py       # Upload CSVs to GCS
|   +-- load_reference_data.py           # Load reference tables
|   +-- build_silver_layer.py            # Execute Silver transforms
|   +-- build_gold_layer.py              # Create star schema
|   +-- build_aggregations.py            # Create KPI tables
|   +-- verify_infrastructure.py         # End-to-end validation
+-- sql/
|   +-- bronze/                 # Raw table definitions (partitioned)
|   +-- silver/                 # Cleaning and normalization (3 scripts)
|   +-- gold/                   # Star schema + aggregations (9 scripts)
+-- tests/
|   +-- unit/                   # Unit tests (22 test cases)
+-- config/
|   +-- project_config.yaml     # GCP project configuration
+-- docs/                       # Technical documentation
+-- .claude/
    +-- agents/                 # 40+ specialized agents
    +-- kb/                     # 7-domain knowledge base
    +-- notes/                  # Requirements and task tracking
    +-- commands/               # Workflow commands
```

---

## Knowledge Base

The project includes a knowledge base with reference patterns across 7 domains, used as development guidance for Claude Code agents:

| Domain         | Description                                  | Key Patterns                                                           |
| -------------- | -------------------------------------------- | ---------------------------------------------------------------------- |
| **Pydantic**   | Python data validation patterns              | `llm-output-validation`, `extraction-schema`, `error-handling`         |
| **GCP**        | Serverless services for event-driven pipes   | `event-driven-pipeline`, `multi-bucket-pipeline`, `cloud-run-scaling`  |
| **Gemini**     | Multimodal LLM for document extraction       | `invoice-extraction`, `structured-json-output`, `openrouter-fallback`  |
| **LangFuse**   | LLMOps observability platform                | `python-sdk-integration`, `cloud-run-instrumentation`, `quality-loops` |
| **Terraform**  | Infrastructure as Code for GCP               | `cloud-run-module`, `pubsub-module`, `remote-state`                    |
| **Terragrunt** | Multi-environment orchestration              | `multi-environment-config`, `dry-hierarchies`, `dependency-management` |
| **CrewAI**     | Multi-agent orchestration for DataOps        | `triage-investigation-report`, `log-analysis-agent`, `slack-integration` |

> **Note:** These knowledge base domains serve as reference documentation and development patterns for Claude Code agents. Not all technologies documented in the KB are implemented in the current version of the project.

---

## Agent System

### Agent Categories

| Category             | Agents                                                                                       | Purpose                              |
| -------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------ |
| **Exploration**      | `codebase-explorer`, `kb-architect`                                                          | Codebase analysis, KB design         |
| **AI/ML**            | `ai-data-engineer`, `llm-specialist`, `genai-architect`, `ai-prompt-specialist`              | LLM development, prompt engineering  |
| **Data Engineering** | `medallion-architect`, `spark-specialist`, `lakeflow-*`, `spark-*`                           | Data pipeline architecture           |
| **Code Quality**     | `code-reviewer`, `code-cleaner`, `test-generator`, `python-developer`                        | Quality assurance, testing           |
| **Communication**    | `the-planner`, `adaptive-explainer`, `meeting-analyst`                                       | Planning, documentation              |
| **Domain**           | `extraction-specialist`, `pipeline-architect`, `function-developer`, `infra-deployer`        | Project-specific implementation      |
| **Workflow**         | `brainstorm-agent`, `define-agent`, `design-agent`, `build-agent`, `iterate-agent`, `ship-agent` | Development lifecycle stages     |
| **Dev**              | `dev-loop-executor`, `prompt-crafter`                                                        | Development iteration                |

---

## Technology Stack

| Layer                 | Technology                     | Purpose                              |
| --------------------- | ------------------------------ | ------------------------------------ |
| **Cloud**             | Google Cloud Platform          | Primary infrastructure               |
| **Compute**           | Cloud Functions (2nd Gen)      | Serverless CSV processing            |
| **Storage**           | GCS                            | File storage (raw, quarantine)       |
| **Data Warehouse**    | BigQuery                       | Medallion architecture (Bronze/Silver/Gold) |
| **Data Processing**   | pandas                         | CSV validation and transformation    |
| **Testing**           | pytest                         | Unit testing with 97.2% coverage     |
| **Code Quality**      | ruff                           | Linting and formatting               |
| **Configuration**     | YAML                           | Project and pipeline configuration   |

---

## Success Metrics

| Metric                         | Target   | Method                    |
| ------------------------------ | -------- | ------------------------- |
| CSV validation accuracy        | >= 99%   | Schema validation checks  |
| Processing latency P95         | < 30s    | Cloud Monitoring          |
| Pipeline availability          | > 99%    | Uptime monitoring         |
| Test coverage                  | > 95%    | pytest-cov                |

---

## Documentation

| Document                                                       | Description                                        |
| -------------------------------------------------------------- | -------------------------------------------------- |
| [Requirements Document](.claude/notes/summary-requirements.md) | Consolidated requirements from planning meetings   |
| [Architecture](../docs/ARCHITECTURE.md)                        | Technical architecture documentation               |
| [Data Architecture](../docs/DATA_ARCHITECTURE.md)              | Data model and medallion layers                    |
| [Setup Guide](../docs/SETUP_GUIDE.md)                          | Step-by-step replication guide                     |
| [Knowledge Base Index](.claude/kb/_index.yaml)                 | Registry of all KB domains and patterns            |
| [Agent System](.claude/agents/)                                | 40+ specialized agents for development             |

---

## Cost Estimates

| Component          | Monthly (Dev)         | Monthly (Prod)          |
| ------------------ | --------------------- | ----------------------- |
| Cloud Functions    | $0-5                  | $5-15                   |
| GCS                | ~$1                   | ~$3                     |
| BigQuery           | ~$5                   | ~$10                    |
| **Total**          | **~$6-11/month**      | **~$18-28/month**       |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Use Claude Code agents for development (`/agent code-reviewer` before committing)
4. Commit your changes following conventional commits
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Anthropic** for Claude Code and the agentic development paradigm
- **Google Cloud** for Cloud Functions and BigQuery infrastructure

---

> *"Do Zero a Producao"* - From Zero to Production, powered by AI-assisted development.
