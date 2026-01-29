-- Case Fictício - Teste -- Gold Layer: Order Items Fact Table
-- ===================================================
--
-- Item-level fact table for detailed product analysis.
-- Supports product mix, pricing, and quantity analysis.
--
-- Grain: One row per order item (line item)
-- Partitioning: By order_date for performance
-- Clustering: By product_key for product analysis
--
-- Author: Arthur Graf -- Case Fictício - Teste Project
-- Date: January 2026

CREATE OR REPLACE TABLE `sixth-foundry-485810-e5.case_ficticio_gold.fact_order_items`
PARTITION BY order_date
CLUSTER BY product_key
AS
SELECT
  -- Primary key
  oi.order_item_id AS item_id,

  -- Foreign keys to dimensions
  oi.order_id,
  FORMAT_DATE('%Y%m%d', o.order_date) AS date_key,
  o.order_date,
  o.unit_id AS unit_key,
  oi.product_id AS product_key,

  -- Additive measures
  oi.quantity,
  oi.unit_price,
  oi.total_item_value,

  -- Context from order (degenerate dimensions)
  o.order_type,
  o.order_status,

  -- Non-additive attributes
  oi.observation,

  -- Metadata
  oi._ingest_date

FROM `sixth-foundry-485810-e5.case_ficticio_silver.order_items` oi
JOIN `sixth-foundry-485810-e5.case_ficticio_silver.orders` o
  ON oi.order_id = o.order_id;
