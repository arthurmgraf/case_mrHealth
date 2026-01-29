# TASK_016: BigQuery Scheduled Queries

## Description

Set up BigQuery scheduled queries to automate the daily Silver and Gold layer transformations. Scheduled queries use the BigQuery Data Transfer Service (free). Queries execute in sequence: Silver first, then Gold, using scheduled time offsets.

## Prerequisites

- TASK_002 complete (bigquerydatatransfer API enabled)
- TASK_014 complete (Silver SQL tested manually)
- TASK_015 complete (Gold SQL tested manually)

## Steps

### Step 1: Create Scheduled Query -- Silver Layer Refresh

```bash
# Schedule Silver transformations at 2:00 AM Sao Paulo time daily
bq query --use_legacy_sql=false \
  --schedule="every day 02:00" \
  --display_name="Daily Silver Refresh" \
  --destination_table="" \
  --project_id=case_ficticio-data-mvp \
  '
  -- Silver: Reference Tables
  CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.products` AS
  SELECT id_produto AS product_id, TRIM(nome_produto) AS product_name, CURRENT_TIMESTAMP() AS _updated_at
  FROM `case_ficticio-data-mvp.case_ficticio_bronze.products` WHERE id_produto IS NOT NULL;

  CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.units` AS
  SELECT u.id_unidade AS unit_id, TRIM(u.nome_unidade) AS unit_name,
         s.id_estado AS state_id, TRIM(s.nome_estado) AS state_name,
         c.id_pais AS country_id, TRIM(c.nome_pais) AS country_name,
         CURRENT_TIMESTAMP() AS _updated_at
  FROM `case_ficticio-data-mvp.case_ficticio_bronze.units` u
  LEFT JOIN `case_ficticio-data-mvp.case_ficticio_bronze.states` s ON u.id_estado = s.id_estado
  LEFT JOIN `case_ficticio-data-mvp.case_ficticio_bronze.countries` c ON s.id_pais = c.id_pais
  WHERE u.id_unidade IS NOT NULL;
  '
```

**Note:** BigQuery scheduled queries support only a single SQL statement per schedule. Create separate schedules for each transformation.

### Step 2: Create Individual Scheduled Queries via Console

Since scheduled queries support one statement each, create them via the BigQuery Console:

**Schedule 1: Silver Orders (2:00 AM)**
```sql
CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.orders` AS
SELECT
  o.id_pedido AS order_id,
  o.id_unidade AS unit_id,
  CASE WHEN UPPER(o.tipo_pedido) LIKE '%ONLINE%' THEN 'ONLINE'
       WHEN UPPER(o.tipo_pedido) LIKE '%FISIC%' THEN 'PHYSICAL'
       ELSE 'UNKNOWN' END AS order_type,
  o.status AS order_status,
  o.data_pedido AS order_date,
  EXTRACT(YEAR FROM o.data_pedido) AS order_year,
  EXTRACT(MONTH FROM o.data_pedido) AS order_month,
  ROUND(o.vlr_pedido, 2) AS order_value,
  ROUND(o.taxa_entrega, 2) AS delivery_fee,
  ROUND(o.vlr_pedido - o.taxa_entrega, 2) AS items_subtotal,
  CASE WHEN o.tipo_pedido = 'Loja Online' AND o.endereco_entrega IS NOT NULL AND o.endereco_entrega != ''
       THEN o.endereco_entrega ELSE NULL END AS delivery_address,
  o._source_file, o._ingest_timestamp, o._ingest_date
FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders` o
QUALIFY ROW_NUMBER() OVER (PARTITION BY o.id_pedido ORDER BY o._ingest_timestamp DESC) = 1;
```

**Schedule 2: Silver Order Items (2:05 AM)**
```sql
CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.order_items` AS
SELECT
  oi.id_item_pedido AS order_item_id, oi.id_pedido AS order_id,
  oi.id_produto AS product_id, CAST(oi.qtd AS INT64) AS quantity,
  ROUND(oi.vlr_item, 2) AS unit_price,
  ROUND(CAST(oi.qtd AS INT64) * oi.vlr_item, 2) AS total_item_value,
  CASE WHEN oi.observacao IS NOT NULL AND TRIM(oi.observacao) != '' THEN TRIM(oi.observacao) ELSE NULL END AS observation,
  oi._source_file, oi._ingest_timestamp, oi._ingest_date
FROM `case_ficticio-data-mvp.case_ficticio_bronze.order_items` oi
INNER JOIN `case_ficticio-data-mvp.case_ficticio_bronze.orders` o ON oi.id_pedido = o.id_pedido
QUALIFY ROW_NUMBER() OVER (PARTITION BY oi.id_item_pedido ORDER BY oi._ingest_timestamp DESC) = 1;
```

**Schedule 3: Gold Fact Sales (2:15 AM)**
```sql
CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_gold.fact_sales`
PARTITION BY order_date CLUSTER BY unit_key, order_type AS
SELECT o.order_id, FORMAT_DATE('%Y%m%d', o.order_date) AS date_key, o.order_date,
  o.unit_id AS unit_key, o.order_type, o.order_status,
  o.order_value, o.delivery_fee, o.items_subtotal,
  ia.total_items, ia.distinct_products, ia.total_quantity,
  o.delivery_address, o._ingest_date
FROM `case_ficticio-data-mvp.case_ficticio_silver.orders` o
LEFT JOIN (SELECT order_id, COUNT(*) AS total_items, COUNT(DISTINCT product_id) AS distinct_products,
           SUM(quantity) AS total_quantity FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items` GROUP BY order_id) ia
ON o.order_id = ia.order_id;
```

### Step 3: Verify Scheduled Queries

```bash
# List scheduled queries
bq ls --transfer_config --project_id=case_ficticio-data-mvp --location=US

# Check run history
bq ls --transfer_run --project_id=case_ficticio-data-mvp --location=US <config_id>
```

### Step 4: Manual Trigger for Testing

```bash
# Trigger a scheduled query run manually
bq mk --transfer_run \
  --project_id=case_ficticio-data-mvp \
  --run_time="2026-01-29T02:00:00Z" \
  <config_id>
```

## Schedule Timeline

```
2:00 AM  Silver: reference tables + orders
2:05 AM  Silver: order items
2:10 AM  Silver: states, countries (reference - if separate)
2:15 AM  Gold: fact_sales
2:20 AM  Gold: fact_order_items
2:25 AM  Gold: KPI aggregations (TASK_018)
2:30 AM  Monitoring: quality checks
```

## Acceptance Criteria

- [ ] Scheduled queries created for Silver transformations
- [ ] Scheduled queries created for Gold transformations
- [ ] Execution order ensures Silver completes before Gold starts
- [ ] Manual trigger works for testing
- [ ] Query logs show successful execution

## Cost Impact

| Action | Cost |
|--------|------|
| BigQuery Data Transfer (scheduled queries) | Free |
| Query execution (~2 GB/day) | Free (within 1 TB/month, ~60 GB/month) |
| **Total** | **$0.00** |

---

*TASK_016 of 26 -- Phase 3: Transformation*
