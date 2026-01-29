#!/usr/bin/env python3
"""
Case Fictício - Teste -- Build Silver Layer
=================================

Executes SQL transformations to build the Silver layer from Bronze data.
Silver layer applies data cleaning, normalization, enrichment, and deduplication.

Usage:
    python scripts/build_silver_layer.py
    python scripts/build_silver_layer.py --project sixth-foundry-485810-e5

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


def verify_silver_tables(client, project_id, dataset_id="case_ficticio_silver"):
    """Verify Silver layer tables and row counts."""
    print("\n" + "="*60)
    print("Silver Layer Verification")
    print("="*60)

    tables = [
        "products",
        "units",
        "states",
        "countries",
        "orders",
        "order_items"
    ]

    results = {}
    for table_name in tables:
        table_id = f"{project_id}.{dataset_id}.{table_name}"

        try:
            query = f"SELECT COUNT(*) as row_count FROM `{table_id}`"
            result = client.query(query).result()
            row_count = list(result)[0].row_count
            results[table_name] = row_count
            print(f"  {table_name:15} {row_count:>6} rows")
        except Exception as e:
            print(f"  {table_name:15} [ERROR] {e}")
            results[table_name] = None

    print("="*60)
    return results


def compare_bronze_silver(client, project_id):
    """Compare row counts between Bronze and Silver layers."""
    print("\n" + "="*60)
    print("Bronze vs Silver Comparison")
    print("="*60)

    comparison_query = f"""
    SELECT 'orders' as table_name,
           (SELECT COUNT(*) FROM `{project_id}.case_ficticio_bronze.orders`) as bronze_rows,
           (SELECT COUNT(*) FROM `{project_id}.case_ficticio_silver.orders`) as silver_rows
    UNION ALL
    SELECT 'order_items',
           (SELECT COUNT(*) FROM `{project_id}.case_ficticio_bronze.order_items`),
           (SELECT COUNT(*) FROM `{project_id}.case_ficticio_silver.order_items`)
    UNION ALL
    SELECT 'products',
           (SELECT COUNT(*) FROM `{project_id}.case_ficticio_bronze.products`),
           (SELECT COUNT(*) FROM `{project_id}.case_ficticio_silver.products`)
    UNION ALL
    SELECT 'units',
           (SELECT COUNT(*) FROM `{project_id}.case_ficticio_bronze.units`),
           (SELECT COUNT(*) FROM `{project_id}.case_ficticio_silver.units`)
    """

    try:
        results = client.query(comparison_query).result()
        print(f"  {'Table':<15} {'Bronze':>8} {'Silver':>8} {'Change':>8}")
        print(f"  {'-'*15} {'-'*8} {'-'*8} {'-'*8}")

        for row in results:
            diff = row.silver_rows - row.bronze_rows
            diff_str = f"{diff:+d}" if diff != 0 else "0"
            print(f"  {row.table_name:<15} {row.bronze_rows:>8} {row.silver_rows:>8} {diff_str:>8}")

        print("="*60)

    except Exception as e:
        print(f"  [ERROR] Comparison failed: {e}")


def main():
    # Load config
    try:
        config = load_config()
        default_project = config['project']['id']
        default_dataset = config['bigquery']['datasets']['silver']
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return 1

    parser = argparse.ArgumentParser(
        description="Build Silver layer from Bronze data"
    )
    parser.add_argument(
        "--project",
        default=default_project,
        help=f"GCP project ID (default from config: {default_project})"
    )
    parser.add_argument(
        "--dataset",
        default=default_dataset,
        help=f"Silver dataset (default from config: {default_dataset})"
    )

    args = parser.parse_args()

    print("="*60)
    print("Case Fictício - Teste -- Build Silver Layer")
    print("="*60)
    print(f"Project: {args.project}")
    print(f"Dataset: {args.dataset}")
    print(f"Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize BigQuery client
    client = bigquery.Client(project=args.project)

    # SQL files to execute (in order)
    sql_dir = Path("sql/silver")
    sql_files = [
        (sql_dir / "01_reference_tables.sql", "Reference tables (products, units, states, countries)"),
        (sql_dir / "02_orders.sql", "Orders with date enrichment and normalization"),
        (sql_dir / "03_order_items.sql", "Order items with calculated totals"),
    ]

    # Execute transformations
    print("\n" + "="*60)
    print("Executing Silver Layer Transformations")
    print("="*60)

    success_count = 0
    for sql_file, description in sql_files:
        if execute_sql_file(client, sql_file, description):
            success_count += 1

    # Verify results
    if success_count == len(sql_files):
        verify_silver_tables(client, args.project, args.dataset)
        compare_bronze_silver(client, args.project)

        print("\n[SUCCESS] Silver layer built successfully!")
        print("\nNext: Build Gold layer (star schema)")
        return 0
    else:
        print(f"\n[ERROR] {len(sql_files) - success_count} transformation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
