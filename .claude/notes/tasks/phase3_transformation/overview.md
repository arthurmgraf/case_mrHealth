# Phase 3: Transformation Layer -- Overview

## Summary

Phase 3 builds the Silver and Gold layers using BigQuery SQL transformations. The original strategic plan used Dataform (SQLX) for transformations. For the MVP, we use BigQuery scheduled queries (free) which achieve the same result with simpler tooling. Silver layer cleans and normalizes data; Gold layer builds the star schema dimensional model and KPI aggregations.

## Architecture Decision: Scheduled Queries vs Dataform

| Criteria | Dataform | BigQuery Scheduled Queries | Decision |
|----------|----------|---------------------------|----------|
| Cost | Free (GCP native) | Free (BQ Data Transfer Service) | Both Free |
| Complexity | Requires repo setup, SQLX syntax | Standard SQL, console-managed | Scheduled Queries (simpler) |
| Git Integration | Built-in | Manual (SQL in repo) | Scheduled Queries (MVP) |
| Dependencies | Automatic DAG | Manual ordering via schedule times | Scheduled Queries (MVP) |
| Upgrade Path | Migrate to Dataform when needed | Straightforward migration | Scheduled Queries |

**Decision:** BigQuery Scheduled Queries for MVP. SQL files are stored in the Git repo under `sql/`. When the project matures, migration to Dataform provides Git-native dependency management.

## Objectives

1. Create Silver layer transformations (cleaned, enriched, normalized)
2. Build Gold layer star schema (dimensions + facts)
3. Set up scheduled queries for daily automated execution
4. Implement SQL-based data quality assertions
5. Create KPI aggregation models

## Tasks

| Task ID | Title | Priority | Estimated Time | Status |
|---------|-------|----------|----------------|--------|
| TASK_014 | Silver Layer SQL | HIGH | 3 hours | NOT STARTED |
| TASK_015 | Gold Star Schema | HIGH | 4 hours | NOT STARTED |
| TASK_016 | Scheduled Queries | HIGH | 1 hour | NOT STARTED |
| TASK_017 | Data Quality Assertions | MEDIUM | 2 hours | NOT STARTED |
| TASK_018 | KPI Aggregations | MEDIUM | 2 hours | NOT STARTED |

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| Phase 2 | Upstream | Bronze layer must be populated with data |
| TASK_012 | Direct | Bronze tables must have data |
| TASK_008 | Direct | Reference data must be loaded |
| Phase 4 | Downstream | Dashboards read from Gold layer |

## Free Tier Usage (Phase 3)

| Service | Free Tier Limit | Phase 3 Usage | Notes |
|---------|-----------------|---------------|-------|
| BigQuery Queries | 1 TB/month | ~5 GB/month (transforms) | 99.5% headroom |
| BigQuery Storage | 10 GB | +30 MB (silver/gold tables) | 99.7% headroom |
| Scheduled Queries | Free (BQ DTS) | 3 queries/day | No additional cost |

## Transformation Flow

```
case_ficticio_bronze              case_ficticio_silver              case_ficticio_gold
+----------------+           +----------------+           +------------------+
| orders         |---------->| orders         |---------->| fact_sales       |
| order_items    |---------->| order_items    |---------->| fact_order_items |
| products       |---------->| products       |---------->| dim_product      |
| units          |---------->| units          |---------->| dim_unit         |
| states         |---------->| states         |---------->| dim_geography    |
| countries      |---------->| countries      |           | dim_date         |
+----------------+           +----------------+           | agg_daily_sales  |
                                                          | agg_unit_perf    |
                                                          +------------------+
```

## Acceptance Criteria

- [ ] Silver tables populated with cleaned, normalized data
- [ ] Gold star schema with all dimensions and facts created
- [ ] Scheduled queries configured for daily execution
- [ ] Data quality assertions passing
- [ ] KPI aggregation models producing expected results
- [ ] All queries within free tier limits

---

*Phase 3 of 5 -- Case Fictício - Teste Data Platform MVP*
