# Looker Studio Dashboard Setup Guide

**Case Fictício - Teste Data Platform MVP**

---

## Overview

This guide walks through creating three Looker Studio dashboards connected to the BigQuery Gold layer:

1. **Executive Dashboard** - CEO João Silva (revenue, growth, trends)
2. **Operations Dashboard** - COO Ricardo Martins (units, products, performance)
3. **Pipeline Monitor** - IT Manager Wilson Luiz (data freshness, quality)

**Cost:** $0.00 - Looker Studio is completely free

---

## Prerequisites

- ✅ BigQuery Gold layer populated with data
- ✅ Aggregation tables built: `agg_daily_sales`, `agg_unit_performance`, `agg_product_performance`
- ✅ Google account with access to project `sixth-foundry-485810-e5`

---

## Step 1: Access Looker Studio

1. Navigate to: https://lookerstudio.google.com
2. Sign in with your Google account
3. Click **Create** → **Data Source**

---

## Step 2: Create BigQuery Data Sources

Create the following data sources by connecting to BigQuery:

### Data Source 1: Daily Sales KPIs

- **Name:** `MRH - Daily Sales`
- **Connector:** BigQuery
- **Project:** `sixth-foundry-485810-e5`
- **Dataset:** `case_ficticio_gold`
- **Table:** `agg_daily_sales`

### Data Source 2: Unit Performance

- **Name:** `MRH - Unit Performance`
- **Connector:** BigQuery
- **Project:** `sixth-foundry-485810-e5`
- **Dataset:** `case_ficticio_gold`
- **Table:** `agg_unit_performance`

### Data Source 3: Product Performance

- **Name:** `MRH - Product Performance`
- **Connector:** BigQuery
- **Project:** `sixth-foundry-485810-e5`
- **Dataset:** `case_ficticio_gold`
- **Table:** `agg_product_performance`

### Data Source 4: Sales Details (For drill-down)

- **Name:** `MRH - Fact Sales`
- **Connector:** BigQuery
- **Project:** `sixth-foundry-485810-e5`
- **Dataset:** `case_ficticio_gold`
- **Table:** `fact_sales`

---

## Step 3: Executive Dashboard

### Create New Report

1. Click **Create** → **Report**
2. Select data source: `MRH - Daily Sales`
3. Name the report: **Case Fictício - Teste - Executive Overview**

### Page 1: Revenue Overview

#### Scorecards (Top Row)
Add 4 scorecards side-by-side:

1. **Total Revenue MTD**
   - Metric: `total_revenue`
   - Aggregation: SUM
   - Number format: Currency (BRL)
   - Comparison: Previous month

2. **Total Orders MTD**
   - Metric: `total_orders`
   - Aggregation: SUM
   - Number format: Number
   - Comparison: Previous month

3. **Avg Order Value**
   - Metric: `avg_order_value`
   - Aggregation: AVG
   - Number format: Currency (BRL)

4. **Online Channel %**
   - Metric: `online_pct`
   - Aggregation: AVG
   - Number format: Percent
   - Style: Green if > 25%

#### Revenue Trend Chart
- Chart Type: Time Series
- Date Dimension: `order_date`
- Metric: `total_revenue` (SUM)
- Style: Line chart, smooth curve
- Color: Green (#2E7D32)

#### Revenue by State
- Chart Type: Bar Chart
- Dimension: `state_name` (from `MRH - Unit Performance` joined on date)
- Metric: `total_revenue` (SUM)
- Sort: Descending by revenue
- Limit: Top 10 states

#### Channel Mix Pie Chart
- Chart Type: Pie Chart
- Dimension: Use custom field: `CASE WHEN online_orders > 0 THEN 'Online' ELSE 'Physical' END`
- Metrics: `online_orders`, `physical_orders`
- Style: Donut chart

### Page 2: Growth Analysis

#### MoM Revenue Growth
- Chart Type: Combo Chart
- Dimension: `year_month`
- Metric 1 (Bar): `total_revenue` (SUM)
- Metric 2 (Line): `total_revenue` (SUM) - Previous period comparison
- Style: Bars + line overlay

#### Active Units Trend
- Chart Type: Line Chart
- Dimension: `order_date`
- Metric: `active_units` (AVG)
- Style: Area chart

#### Cancellation Rate Trend
- Chart Type: Line Chart
- Dimension: `order_date`
- Metric: `cancellation_rate` (AVG)
- Style: Red line, threshold at 10%

---

## Step 4: Operations Dashboard

### Create New Report

1. Click **Create** → **Report**
2. Select data source: `MRH - Unit Performance`
3. Name the report: **Case Fictício - Teste - Operations**

### Page 1: Unit Performance

#### Top 10 Units by Revenue
- Chart Type: Bar Chart
- Dimension: `unit_name`
- Metric: `total_revenue` (SUM)
- Sort: Descending
- Limit: 10
- Color: Green gradient

#### Bottom 10 Units
- Chart Type: Bar Chart
- Dimension: `unit_name`
- Metric: `total_revenue` (SUM)
- Sort: Ascending
- Limit: 10
- Color: Red gradient

#### Unit Performance Table
- Chart Type: Table
- Dimensions: `unit_name`, `state_name`
- Metrics: `total_orders`, `total_revenue`, `avg_order_value`, `cancellation_rate`
- Sort: By revenue rank
- Style: Heat map on cancellation_rate (red > 10%)

### Page 2: Product Analysis

Switch data source to: `MRH - Product Performance`

#### Top Products by Revenue
- Chart Type: Bar Chart
- Dimension: `product_name`
- Metric: `total_revenue` (SUM)
- Sort: Descending
- Limit: 20

#### Top Products by Volume
- Chart Type: Bar Chart
- Dimension: `product_name`
- Metric: `total_quantity_sold` (SUM)
- Sort: Descending
- Limit: 20

#### Product Distribution Table
- Chart Type: Table
- Dimensions: `product_name`
- Metrics: `total_orders`, `total_quantity_sold`, `units_selling_product`, `avg_unit_price`
- Sort: By revenue rank

---

## Step 5: Pipeline Monitor Dashboard

### Create New Report

1. Click **Create** → **Report**
2. Select data source: `MRH - Fact Sales`
3. Name the report: **Case Fictício - Teste - Pipeline Monitor**

### Key Metrics Scorecards

1. **Data Freshness**
   - Metric: `MAX(_ingest_date)`
   - Format: Date
   - Alert: Red if > 1 day old

2. **Units Reporting Today**
   - Metric: `COUNT(DISTINCT unit_key)` with filter `_ingest_date = TODAY()`
   - Format: Number
   - Comparison: Previous day

3. **Records Ingested Today**
   - Metric: `COUNT(*)` with filter `_ingest_date = TODAY()`
   - Format: Number

### Daily Ingestion Volume Chart
- Chart Type: Time Series
- Dimension: `_ingest_date`
- Metric: `COUNT(*)`
- Date range: Last 30 days
- Style: Area chart

### Custom Query: Pipeline Health

Add a custom query data source:

```sql
SELECT
  _ingest_date,
  COUNT(DISTINCT unit_key) AS units_reporting,
  COUNT(*) AS total_orders,
  ROUND(SUM(order_value), 2) AS total_revenue,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(CAST(_ingest_date AS TIMESTAMP)), HOUR) AS hours_since_last_ingest
FROM `sixth-foundry-485810-e5.case_ficticio_gold.fact_sales`
WHERE _ingest_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY _ingest_date
ORDER BY _ingest_date DESC
```

Use this for the pipeline health summary table.

---

## Step 6: Dashboard Design & Finishing Touches

### Color Scheme
- Primary: **Green** (#2E7D32) - Health theme
- Secondary: **Light Green** (#66BB6A)
- Alert: **Red** (#D32F2F)
- Background: **White** (#FFFFFF)

### Date Range Filters

Add a date range control to each dashboard:
1. Click **Add a control** → **Date range control**
2. Default range: Last 30 days
3. Position: Top right of dashboard
4. Apply to all charts on the page

### Auto-Refresh

For the Pipeline Monitor dashboard:
1. Click **File** → **Report settings**
2. Enable **Auto-refresh**
3. Interval: 15 minutes
4. Time window: 8 AM - 6 PM (business hours)

### Mobile Layout

1. Click **View** → **Mobile layout**
2. Rearrange widgets for portrait orientation
3. Stack scorecards vertically
4. Charts: Full width

---

## Step 7: Share Dashboards

### With Executives (View Only)

1. Click **Share** button
2. Enter email: `joao.silva@case_ficticio.com`
3. Role: **Viewer**
4. Send

### With Operations Team (Can Edit)

1. Click **Share** button
2. Enter email: `ricardo.martins@case_ficticio.com`
3. Role: **Editor**
4. Send

### Generate Public Link (Optional)

1. Click **Share** → **Get link**
2. Access: **Anyone with the link can view**
3. Copy link for embedding in internal wiki

---

## Step 8: Verify Dashboard Performance

### Check Query Performance

1. Open any chart
2. Click **⋮** (three dots) → **View SQL**
3. Verify query runs in < 5 seconds
4. If slow, check:
   - Aggregation tables are populated
   - Date filters are applied
   - No unnecessary JOINs

### Test Data Refresh

1. Upload new CSV files to GCS to trigger ingestion
2. Wait 2-3 minutes for Cloud Function to process
3. Rebuild Silver/Gold layers:
   ```powershell
   py scripts/build_silver_layer.py
   py scripts/build_gold_layer.py
   py scripts/build_aggregations.py
   ```
4. Refresh Looker Studio dashboard (Ctrl+R)
5. Verify new data appears

---

## Maintenance

### Daily (Automated)

- Cloud Function ingests new CSV files automatically
- Scheduled queries refresh Silver/Gold layers (if configured)

### Weekly (Manual for MVP)

```powershell
# Rebuild transformation layers
py scripts/build_silver_layer.py
py scripts/build_gold_layer.py
py scripts/build_aggregations.py
```

### Monthly

- Review dashboard performance
- Check for slow queries
- Update date filters if needed

---

## Troubleshooting

### Dashboard shows no data

**Issue:** Charts are empty or show "No data"

**Solution:**
1. Check BigQuery tables have data:
   ```sql
   SELECT COUNT(*) FROM `sixth-foundry-485810-e5.case_ficticio_gold.agg_daily_sales`;
   ```
2. Verify date range filter is not too narrow
3. Check data source connection is active

### Slow dashboard load times

**Issue:** Dashboard takes > 10 seconds to load

**Solution:**
1. Use aggregation tables instead of fact tables
2. Add date filters to limit data scanned
3. Enable data caching in Looker Studio settings

### Data is stale (not updating)

**Issue:** Dashboard shows yesterday's data

**Solution:**
1. Check Cloud Function is running:
   ```powershell
   gcloud functions logs read csv-processor --gen2 --region=us-central1
   ```
2. Rebuild Silver/Gold layers manually
3. Check BigQuery `_ingest_date` field

---

## Cost Monitoring

**Expected Costs:** $0.00

- Looker Studio: Free (unlimited)
- BigQuery queries from dashboards: ~5 GB/month (well within 1 TB free tier)

**Monitor usage:**
```sql
-- Check query bytes scanned by Looker Studio
SELECT
  user_email,
  SUM(total_bytes_processed) / 1e12 AS tb_processed
FROM `sixth-foundry-485810-e5.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND user_email LIKE '%looker%'
GROUP BY user_email;
```

---

## Next Steps

- ✅ Dashboards created and shared
- ⏭️ Set up monitoring alerts (Phase 4, Task 20)
- ⏭️ Configure scheduled queries for automated refresh
- ⏭️ Create end-user training materials

---

**Documentation Version:** 1.0
**Last Updated:** 2026-01-29
**Author:** Arthur Graf Team
