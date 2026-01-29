# TASK_019: Looker Studio Dashboard Setup

## Description

Create Looker Studio dashboards connected to the BigQuery Gold layer. Three dashboards serve three personas: Executive (CEO Joao), Operations (COO Ricardo), and Pipeline Monitoring (IT Wilson). Looker Studio is completely free.

## Prerequisites

- Phase 3 complete (Gold layer and KPI tables populated)

## Steps

### Step 1: Create Data Sources in Looker Studio

Navigate to https://lookerstudio.google.com and create data sources:

| Data Source Name | BigQuery Table | Purpose |
|-----------------|----------------|---------|
| MRH - Daily Sales | case_ficticio_gold.agg_daily_sales | Executive + Operations dashboards |
| MRH - Unit Performance | case_ficticio_gold.agg_unit_performance | Operations dashboard |
| MRH - Product Performance | case_ficticio_gold.agg_product_performance | Operations dashboard |
| MRH - Fact Sales | case_ficticio_gold.fact_sales | Drill-down queries |
| MRH - Pipeline Runs | case_ficticio_monitoring.pipeline_runs | IT dashboard |
| MRH - Quality Checks | case_ficticio_monitoring.quality_checks | IT dashboard |

### Step 2: Executive Dashboard (CEO -- Joao Silva)

**Dashboard Name:** Case Fictício - Teste Executive Overview

**Page 1: Revenue Overview**
| Visual | Type | Data Source | Fields |
|--------|------|-------------|--------|
| Total Revenue (MTD) | Scorecard | agg_daily_sales | SUM(total_revenue) |
| Total Orders (MTD) | Scorecard | agg_daily_sales | SUM(total_orders) |
| Avg Order Value | Scorecard | agg_daily_sales | AVG(avg_order_value) |
| Online % | Scorecard | agg_daily_sales | AVG(online_pct) |
| Revenue Trend | Time Series | agg_daily_sales | order_date, total_revenue |
| Revenue by State | Bar Chart | agg_daily_sales | state_name, SUM(total_revenue) |
| Channel Mix (Online vs Physical) | Pie Chart | agg_daily_sales | online_orders, physical_orders |

**Page 2: Growth Analysis**
| Visual | Type | Data Source | Fields |
|--------|------|-------------|--------|
| MoM Revenue Growth | Combo Chart | agg_daily_sales | year_month, total_revenue |
| Active Units Trend | Line Chart | agg_daily_sales | order_date, active_units |
| Cancellation Rate Trend | Line Chart | agg_daily_sales | order_date, cancellation_rate |
| Weekend vs Weekday Revenue | Grouped Bar | agg_daily_sales | is_weekend, SUM(total_revenue) |

### Step 3: Operations Dashboard (COO -- Ricardo Martins)

**Dashboard Name:** Case Fictício - Teste Operations

**Page 1: Unit Performance**
| Visual | Type | Data Source | Fields |
|--------|------|-------------|--------|
| Unit Revenue Ranking | Table | agg_unit_performance | unit_name, total_revenue, revenue_rank |
| Top 10 Units | Bar Chart | agg_unit_performance | unit_name, total_revenue (sorted) |
| Bottom 10 Units | Bar Chart | agg_unit_performance | unit_name, total_revenue (sorted ASC) |
| Cancellation by Unit | Heat Map | agg_unit_performance | unit_name, cancellation_rate |

**Page 2: Product Analysis**
| Visual | Type | Data Source | Fields |
|--------|------|-------------|--------|
| Top Products by Revenue | Bar Chart | agg_product_performance | product_name, total_revenue |
| Top Products by Volume | Bar Chart | agg_product_performance | product_name, total_quantity_sold |
| Product Distribution | Table | agg_product_performance | product_name, units_selling_product |

### Step 4: Pipeline Dashboard (IT -- Wilson Luiz)

**Dashboard Name:** Case Fictício - Teste Pipeline Monitor

| Visual | Type | Data Source | Fields |
|--------|------|-------------|--------|
| Data Freshness | Scorecard | fact_sales | MAX(_ingest_date) |
| Units Reporting Today | Scorecard | Custom Query | COUNT(DISTINCT unit_key) today |
| Quality Check Results | Table | quality_checks | check_name, result, details |
| Daily Ingestion Volume | Time Series | Custom Query | _ingest_date, COUNT(*) |

### Step 5: Custom BigQuery Query for Pipeline Dashboard

Add this as a Custom Query data source:

```sql
-- Pipeline health summary
SELECT
  _ingest_date,
  COUNT(DISTINCT unit_key) AS units_reporting,
  COUNT(*) AS total_orders,
  SUM(order_value) AS total_revenue,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(CAST(_ingest_date AS TIMESTAMP)), HOUR) AS hours_since_last
FROM `case_ficticio-data-mvp.case_ficticio_gold.fact_sales`
WHERE _ingest_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY _ingest_date
ORDER BY _ingest_date DESC;
```

## Dashboard Design Guidelines

1. **Color scheme**: Use Case Fictício - Teste brand colors (green tones for health theme)
2. **Date filters**: Every dashboard has a date range selector (default: last 30 days)
3. **Auto-refresh**: Enable auto-refresh every 15 minutes during business hours
4. **Mobile**: Design for responsive layout (executives check on mobile)

## Acceptance Criteria

- [ ] Executive dashboard shows revenue, orders, channel mix, and trends
- [ ] Operations dashboard shows unit rankings and product performance
- [ ] Pipeline dashboard shows data freshness and quality checks
- [ ] All dashboards connect to BigQuery Gold layer
- [ ] Date range filters work correctly
- [ ] Dashboards load within 5 seconds

## Cost Impact

| Action | Cost |
|--------|------|
| Looker Studio | Free (unlimited) |
| BigQuery queries from dashboards (~5 GB/month) | Free (within 1 TB/month) |
| **Total** | **$0.00** |

---

*TASK_019 of 26 -- Phase 4: Consumption*
