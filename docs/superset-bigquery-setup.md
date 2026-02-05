# Superset <-> BigQuery Connection Guide

> Step-by-step guide to connect Apache Superset to BigQuery Gold and Monitoring datasets.

## Prerequisites

- Superset running (Docker or K3s)
- GCP Service Account JSON file with `bigquery.dataViewer` + `bigquery.jobUser` roles
- Service Account file mounted at `/app/keys/gcp.json` inside the Superset container

## 1. Verify Service Account Mount

```bash
# Docker Compose
docker compose -f docker-compose-superset.yml exec superset ls -la /app/keys/
# Expected: gcp.json

# K3s
kubectl exec -n mrhealth-superset deploy/superset -- ls -la /app/keys/
```

## 2. Install sqlalchemy-bigquery

The Superset Dockerfile already includes `sqlalchemy-bigquery`. Verify:

```bash
docker compose -f docker-compose-superset.yml exec superset pip show sqlalchemy-bigquery
```

If missing, add to `superset/Dockerfile`:
```dockerfile
RUN pip install sqlalchemy-bigquery
```

## 3. Create Database Connections

### 3.1 Access Superset UI

```
http://localhost:8088  (Docker)
http://K3S-NODE-IP:30188  (K3s)

Login: admin / admin (change in production)
```

### 3.2 Add BigQuery Gold Connection

1. Navigate to **Settings** > **Database Connections** > **+ Database**
2. Select **Google BigQuery**
3. Fill in:
   - **Display Name:** `MR Health BigQuery Gold`
   - **SQLAlchemy URI:**
     ```
     bigquery://sixth-foundry-485810-e5/case_ficticio_gold
     ```
   - **Engine Parameters (JSON):**
     ```json
     {
       "credentials_path": "/app/keys/gcp.json"
     }
     ```
4. Click **Test Connection** - should show "Connection looks good!"
5. Click **Connect**

### 3.3 Add BigQuery Monitoring Connection

Repeat with:
- **Display Name:** `MR Health BigQuery Monitoring`
- **SQLAlchemy URI:**
  ```
  bigquery://sixth-foundry-485810-e5/case_ficticio_monitoring
  ```
- Same Engine Parameters

## 4. Create Datasets (10 total)

Navigate to **Datasets** > **+ Dataset** for each:

### Gold Datasets (9)

| Dataset Name | Database | Schema | Table |
|---|---|---|---|
| `gold__fact_sales` | MR Health BigQuery Gold | case_ficticio_gold | fact_sales |
| `gold__fact_order_items` | MR Health BigQuery Gold | case_ficticio_gold | fact_order_items |
| `gold__dim_date` | MR Health BigQuery Gold | case_ficticio_gold | dim_date |
| `gold__dim_product` | MR Health BigQuery Gold | case_ficticio_gold | dim_product |
| `gold__dim_unit` | MR Health BigQuery Gold | case_ficticio_gold | dim_unit |
| `gold__dim_geography` | MR Health BigQuery Gold | case_ficticio_gold | dim_geography |
| `gold__agg_daily_sales` | MR Health BigQuery Gold | case_ficticio_gold | agg_daily_sales |
| `gold__agg_unit_performance` | MR Health BigQuery Gold | case_ficticio_gold | agg_unit_performance |
| `gold__agg_product_performance` | MR Health BigQuery Gold | case_ficticio_gold | agg_product_performance |

### Monitoring Dataset (1)

| Dataset Name | Database | Schema | Table |
|---|---|---|---|
| `monitoring__data_quality_log` | MR Health BigQuery Monitoring | case_ficticio_monitoring | data_quality_log |

## 5. Create Dashboards (4)

### 5.1 Executive Overview

**Source:** `gold__agg_daily_sales`

Charts:
- **Line Chart:** Daily Revenue Trend (x: order_date, y: SUM(total_revenue))
- **Big Number:** Total Revenue Today
- **Bar Chart:** Top 10 Units by Revenue (from `gold__agg_unit_performance`)
- **Table:** Daily Summary (date, orders, revenue, avg_ticket)

### 5.2 Operations

**Source:** `gold__fact_sales`

Charts:
- **Pie Chart:** Order Status Distribution
- **Bar Chart:** Orders by Hour (order_date grouped by hour)
- **Big Number:** Average Delivery Fee
- **Table:** Recent Orders (order_id, unit_key, order_value, status)

Filters: date range, unit_key, order_status

### 5.3 Product Analytics

**Source:** `gold__agg_product_performance`

Charts:
- **Bar Chart:** Top 20 Products by Revenue
- **Treemap:** Product Revenue Share
- **Line Chart:** Product Trend (orders per day per product)
- **Table:** Product Performance (name, total_orders, total_revenue, avg_price)

### 5.4 Data Quality

**Source:** `monitoring__data_quality_log`

Charts:
- **Big Number:** Quality Score % (COUNTIF(result='pass') / COUNT(*) * 100)
- **Table:** Latest Check Results (check_name, result, actual_value, duration)
- **Line Chart:** Quality Score History (by execution_date)
- **Bar Chart:** Failures by Category

## 6. Validation Checklist

```
[ ] Test Connection returns "Connection looks good!" for both databases
[ ] All 10 datasets show row counts > 0
[ ] Executive dashboard loads with real data
[ ] Operations dashboard filters work
[ ] Product Analytics shows top products
[ ] Data Quality shows check results
[ ] No timeout errors on large queries
```

## 7. Troubleshooting

| Issue | Solution |
|---|---|
| "Could not connect" | Check service account mount: `ls /app/keys/gcp.json` |
| "Permission denied" | Verify SA has `bigquery.dataViewer` + `bigquery.jobUser` roles |
| "Dataset not found" | Check dataset name in URI matches BigQuery exactly |
| Slow queries | Add date filters to dashboards, use agg_ tables instead of fact_ |
| Empty charts | Run `bq ls case_ficticio_gold` to verify tables have data |
