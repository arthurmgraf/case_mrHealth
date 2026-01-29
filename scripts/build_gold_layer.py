#!/usr/bin/env python3
"""
Case Fictício - Teste -- Build Gold Layer (Star Schema)
=============================================

Executes SQL transformations to build the Gold layer star schema from Silver data.
Creates dimension tables (date, product, unit, geography) and fact tables (sales, order_items).

Usage:
    python scripts/build_gold_layer.py
    python scripts/build_gold_layer.py --project sixth-foundry-485810-e5

Requirements:
    pip install google-cloud-bigquery pyyaml

Author: Arthur Graf -- Case Fictício - Teste Project
Date: January 2026
"""

import argparse
import sys
import yaml
from pathlib import Path
from google.cloud import bigquery
from datetime import datetime


def load_config():
    """Load project configuration from YAML."""
    config_path = Path("config/project_config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def execute_sql_file(client, sql_file_path: Path, description: str):
    """Execute a SQL file in BigQuery."""
    print(f"\n[EXECUTING] {description}")
    print(f"  File: {sql_file_path.name}")

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Execute query
        query_job = client.query(sql)
        query_job.result()  # Wait for completion

        # Get statistics
        bytes_processed = query_job.total_bytes_processed or 0
        bytes_billed = query_job.total_bytes_billed or 0

        print(f"  [OK] Query completed")
        print(f"       Bytes processed: {bytes_processed:,}")
        print(f"       Bytes billed: {bytes_billed:,}")

        return True

    except Exception as e:
        print(f"  [ERROR] Query failed: {e}")
        return False


def verify_gold_layer(client, project_id, dataset_id="case_ficticio_gold"):
    """Verify Gold layer tables and row counts."""
    print("\n" + "="*60)
    print("Gold Layer Verification")
    print("="*60)

    tables = {
        "Dimensions": ["dim_date", "dim_product", "dim_unit", "dim_geography"],
        "Facts": ["fact_sales", "fact_order_items"]
    }

    results = {}
    for category, table_list in tables.items():
        print(f"\n{category}:")
        for table_name in table_list:
            table_id = f"{project_id}.{dataset_id}.{table_name}"

            try:
                query = f"SELECT COUNT(*) as row_count FROM `{table_id}`"
                result = client.query(query).result()
                row_count = list(result)[0].row_count
                results[table_name] = row_count
                print(f"  {table_name:20} {row_count:>8} rows")
            except Exception as e:
                print(f"  {table_name:20} [ERROR] {e}")
                results[table_name] = None

    print("="*60)
    return results


def test_star_schema_join(client, project_id, dataset_id="case_ficticio_gold"):
    """Test a simple star schema join to validate the model."""
    print("\n" + "="*60)
    print("Star Schema Join Test")
    print("="*60)

    test_query = f"""
    SELECT
      d.year_month,
      u.state_name,
      u.unit_name,
      COUNT(DISTINCT f.order_id) AS total_orders,
      SUM(f.order_value) AS total_revenue,
      ROUND(AVG(f.order_value), 2) AS avg_order_value
    FROM `{project_id}.{dataset_id}.fact_sales` f
    JOIN `{project_id}.{dataset_id}.dim_date` d
      ON f.date_key = d.date_key
    JOIN `{project_id}.{dataset_id}.dim_unit` u
      ON f.unit_key = u.unit_key
    GROUP BY d.year_month, u.state_name, u.unit_name
    ORDER BY total_revenue DESC
    LIMIT 10
    """

    try:
        print("Running sample analytics query...")
        results = client.query(test_query).result()

        print(f"\n{'Year-Month':<12} {'State':<15} {'Unit':<20} {'Orders':>8} {'Revenue':>12} {'Avg Order':>10}")
        print("-" * 90)

        row_count = 0
        for row in results:
            print(f"{row.year_month or 'N/A':<12} {row.state_name or 'N/A':<15} {row.unit_name or 'N/A':<20} "
                  f"{row.total_orders:>8} {row.total_revenue:>12.2f} {row.avg_order_value:>10.2f}")
            row_count += 1

        if row_count == 0:
            print("(No data - tables are empty, awaiting Cloud Function ingestion)")

        print("="*60)
        print("[OK] Star schema join successful!")
        return True

    except Exception as e:
        print(f"[ERROR] Star schema join failed: {e}")
        return False


def main():
    # Load config
    try:
        config = load_config()
        default_project = config['project']['id']
        default_dataset = config['bigquery']['datasets']['gold']
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return 1

    parser = argparse.ArgumentParser(
        description="Build Gold layer star schema from Silver data"
    )
    parser.add_argument(
        "--project",
        default=default_project,
        help=f"GCP project ID (default from config: {default_project})"
    )
    parser.add_argument(
        "--dataset",
        default=default_dataset,
        help=f"Gold dataset (default from config: {default_dataset})"
    )

    args = parser.parse_args()

    print("="*60)
    print("Case Fictício - Teste -- Build Gold Layer (Star Schema)")
    print("="*60)
    print(f"Project: {args.project}")
    print(f"Dataset: {args.dataset}")
    print(f"Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize BigQuery client
    client = bigquery.Client(project=args.project)

    # SQL files to execute (in dependency order)
    sql_dir = Path("sql/gold")
    sql_files = [
        (sql_dir / "01_dim_date.sql", "Date dimension (2025-2027)"),
        (sql_dir / "02_dim_product.sql", "Product dimension"),
        (sql_dir / "03_dim_unit.sql", "Unit dimension with geography"),
        (sql_dir / "04_dim_geography.sql", "Geography dimension"),
        (sql_dir / "05_fact_sales.sql", "Sales fact table (order-level)"),
        (sql_dir / "06_fact_order_items.sql", "Order items fact table (line-level)"),
    ]

    # Execute transformations
    print("\n" + "="*60)
    print("Executing Gold Layer Transformations")
    print("="*60)

    success_count = 0
    for sql_file, description in sql_files:
        if execute_sql_file(client, sql_file, description):
            success_count += 1

    # Verify results
    if success_count == len(sql_files):
        verify_gold_layer(client, args.project, args.dataset)
        test_star_schema_join(client, args.project, args.dataset)

        print("\n[SUCCESS] Gold layer (star schema) built successfully!")
        print("\nNext: Set up scheduled queries for automated refresh")
        return 0
    else:
        print(f"\n[ERROR] {len(sql_files) - success_count} transformation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
