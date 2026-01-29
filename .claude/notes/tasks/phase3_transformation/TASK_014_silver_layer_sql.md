# TASK_014: Silver Layer SQL Transformations

## Description

Create BigQuery SQL transformations that move data from Bronze to Silver layer. Silver layer applies business rules, normalizes data, enriches with reference data joins, and prepares clean datasets for the Gold dimensional model.

## Prerequisites

- Phase 2 complete (Bronze tables populated)
- TASK_008 complete (Reference data loaded)

## SQL Transformations

### Silver Orders

Create `sql/silver/orders.sql`:

```sql
-- Silver Layer: Orders
-- Source: case_ficticio_bronze.orders
-- Transformations: type normalization, business rules, enrichment

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.orders` AS
SELECT
  -- Primary key
  o.id_pedido AS order_id,

  -- Dimensions
  o.id_unidade AS unit_id,
  CASE
    WHEN UPPER(o.tipo_pedido) LIKE '%ONLINE%' THEN 'ONLINE'
    WHEN UPPER(o.tipo_pedido) LIKE '%FISIC%' THEN 'PHYSICAL'
    ELSE 'UNKNOWN'
  END AS order_type,
  o.status AS order_status,

  -- Date fields
  o.data_pedido AS order_date,
  EXTRACT(YEAR FROM o.data_pedido) AS order_year,
  EXTRACT(MONTH FROM o.data_pedido) AS order_month,
  EXTRACT(DAY FROM o.data_pedido) AS order_day,
  FORMAT_DATE('%A', o.data_pedido) AS order_day_of_week,

  -- Monetary fields
  ROUND(o.vlr_pedido, 2) AS order_value,
  ROUND(o.taxa_entrega, 2) AS delivery_fee,
  ROUND(o.vlr_pedido - o.taxa_entrega, 2) AS items_subtotal,

  -- Delivery info
  CASE
    WHEN o.tipo_pedido = 'Loja Online' AND (o.endereco_entrega IS NOT NULL AND o.endereco_entrega != '')
    THEN o.endereco_entrega
    ELSE NULL
  END AS delivery_address,

  -- Metadata
  o._source_file,
  o._ingest_timestamp,
  o._ingest_date

FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders` o

-- Deduplication: keep latest ingestion per order
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY o.id_pedido
  ORDER BY o._ingest_timestamp DESC
) = 1;
```

### Silver Order Items

Create `sql/silver/order_items.sql`:

```sql
-- Silver Layer: Order Items
-- Source: case_ficticio_bronze.order_items
-- Transformations: calculated fields, type casting, enrichment

CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.order_items` AS
SELECT
  -- Primary key
  oi.id_item_pedido AS order_item_id,

  -- Foreign keys
  oi.id_pedido AS order_id,
  oi.id_produto AS product_id,

  -- Measures
  CAST(oi.qtd AS INT64) AS quantity,
  ROUND(oi.vlr_item, 2) AS unit_price,
  ROUND(CAST(oi.qtd AS INT64) * oi.vlr_item, 2) AS total_item_value,

  -- Descriptive
  CASE
    WHEN oi.observacao IS NOT NULL AND TRIM(oi.observacao) != ''
    THEN TRIM(oi.observacao)
    ELSE NULL
  END AS observation,

  -- Metadata
  oi._source_file,
  oi._ingest_timestamp,
  oi._ingest_date

FROM `case_ficticio-data-mvp.case_ficticio_bronze.order_items` oi

-- Only include items that have matching orders (referential integrity)
INNER JOIN `case_ficticio-data-mvp.case_ficticio_bronze.orders` o
  ON oi.id_pedido = o.id_pedido

-- Deduplication
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY oi.id_item_pedido
  ORDER BY oi._ingest_timestamp DESC
) = 1;
```

### Silver Reference Tables

Create `sql/silver/reference_tables.sql`:

```sql
-- Silver Layer: Products
CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.products` AS
SELECT
  id_produto AS product_id,
  TRIM(nome_produto) AS product_name,
  CURRENT_TIMESTAMP() AS _updated_at
FROM `case_ficticio-data-mvp.case_ficticio_bronze.products`
WHERE id_produto IS NOT NULL;

-- Silver Layer: Units (enriched with state)
CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.units` AS
SELECT
  u.id_unidade AS unit_id,
  TRIM(u.nome_unidade) AS unit_name,
  s.id_estado AS state_id,
  TRIM(s.nome_estado) AS state_name,
  c.id_pais AS country_id,
  TRIM(c.nome_pais) AS country_name,
  CURRENT_TIMESTAMP() AS _updated_at
FROM `case_ficticio-data-mvp.case_ficticio_bronze.units` u
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_bronze.states` s
  ON u.id_estado = s.id_estado
LEFT JOIN `case_ficticio-data-mvp.case_ficticio_bronze.countries` c
  ON s.id_pais = c.id_pais
WHERE u.id_unidade IS NOT NULL;

-- Silver Layer: States
CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.states` AS
SELECT
  id_estado AS state_id,
  id_pais AS country_id,
  TRIM(nome_estado) AS state_name,
  CURRENT_TIMESTAMP() AS _updated_at
FROM `case_ficticio-data-mvp.case_ficticio_bronze.states`
WHERE id_estado IS NOT NULL;

-- Silver Layer: Countries
CREATE OR REPLACE TABLE `case_ficticio-data-mvp.case_ficticio_silver.countries` AS
SELECT
  id_pais AS country_id,
  TRIM(nome_pais) AS country_name,
  CURRENT_TIMESTAMP() AS _updated_at
FROM `case_ficticio-data-mvp.case_ficticio_bronze.countries`
WHERE id_pais IS NOT NULL;
```

## Execution

### Manual Execution

```bash
# Execute Silver transformations in order
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/silver/reference_tables.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/silver/orders.sql
bq query --use_legacy_sql=false --project_id=case_ficticio-data-mvp < sql/silver/order_items.sql
```

### Verification

```sql
-- Row counts comparison: Bronze vs Silver
SELECT
  'bronze_orders' as table_name, COUNT(*) as rows FROM `case_ficticio-data-mvp.case_ficticio_bronze.orders`
UNION ALL
SELECT 'silver_orders', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_silver.orders`
UNION ALL
SELECT 'bronze_items', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_bronze.order_items`
UNION ALL
SELECT 'silver_items', COUNT(*) FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items`;

-- Verify enrichment worked
SELECT unit_id, unit_name, state_name, country_name
FROM `case_ficticio-data-mvp.case_ficticio_silver.units`
LIMIT 10;

-- Verify calculated fields
SELECT order_id, quantity, unit_price, total_item_value,
       ROUND(quantity * unit_price, 2) as expected_total,
       total_item_value = ROUND(quantity * unit_price, 2) as calc_correct
FROM `case_ficticio-data-mvp.case_ficticio_silver.order_items`
LIMIT 10;
```

## Acceptance Criteria

- [ ] Silver orders table created with normalized types (ONLINE/PHYSICAL)
- [ ] Silver order items table has calculated total_item_value
- [ ] Reference tables enriched (units joined with states and countries)
- [ ] Deduplication applied (ROW_NUMBER window function)
- [ ] Referential integrity enforced (only items with matching orders)
- [ ] Row counts match or are lower than Bronze (cleaning removes invalid rows)

## Cost Impact

| Action | Cost |
|--------|------|
| CREATE OR REPLACE queries (~500 MB scanned) | Free (within 1 TB/month) |
| Silver table storage (~40 MB) | Free (within 10 GB) |
| **Total** | **$0.00** |

---

*TASK_014 of 26 -- Phase 3: Transformation*
