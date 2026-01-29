#!/usr/bin/env python3
"""
Case Fictício - Teste -- Build KPI Aggregation Tables
===========================================

Creates pre-aggregated tables for dashboard performance.
These tables power the Looker Studio dashboards.

Usage:
    python scripts/build_aggregations.py

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


def verify_aggregations(client, project_id, dataset_id="case_ficticio_gold"):
    """Verify aggregation tables and row counts."""
    print("\n" + "="*60)
    print("Aggregation Tables Verification")
    print("="*60)

    tables = [
        "agg_daily_sales",
        "agg_unit_performance",
        "agg_product_performance"
    ]

    results = {}
    for table_name in tables:
        table_id = f"{project_id}.{dataset_id}.{table_name}"

        try:
            query = f"SELECT COUNT(*) as row_count FROM `{table_id}`"
            result = client.query(query).result()
            row_count = list(result)[0].row_count
            results[table_name] = row_count
            print(f"  {table_name:30} {row_count:>6} rows")
        except Exception as e:
            print(f"  {table_name:30} [ERROR] {e}")
            results[table_name] = None

    print("="*60)
    return results


def show_sample_data(client, project_id, dataset_id="case_ficticio_gold"):
    """Show sample data from aggregation tables."""
    print("\n" + "="*60)
    print("Sample Data - Daily Sales")
    print("="*60)

    sample_query = f"""
    SELECT
      order_date,
      total_orders,
      total_revenue,
      avg_order_value,
      online_pct,
      cancellation_rate
    FROM `{project_id}.{dataset_id}.agg_daily_sales`
    ORDER BY order_date DESC
    LIMIT 5
    """

    try:
        results = client.query(sample_query).result()

        print(f"\n{'Date':<12} {'Orders':>8} {'Revenue':>12} {'Avg Order':>10} {'Online %':>9} {'Cancel %':>9}")
        print("-" * 72)

        for row in results:
            print(f"{str(row.order_date):<12} {row.total_orders:>8} "
                  f"{row.total_revenue:>12.2f} {row.avg_order_value:>10.2f} "
                  f"{row.online_pct:>8.1f}% {row.cancellation_rate:>8.1f}%")

    except Exception as e:
        print(f"[ERROR] Sample query failed: {e}")


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
        description="Build KPI aggregation tables for dashboards"
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
    print("Case Fictício - Teste -- Build KPI Aggregations")
    print("="*60)
    print(f"Project: {args.project}")
    print(f"Dataset: {args.dataset}")
    print(f"Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize BigQuery client
    client = bigquery.Client(project=args.project)

    # SQL files to execute (in order)
    sql_dir = Path("sql/gold")
    sql_files = [
        (sql_dir / "07_agg_daily_sales.sql", "Daily sales aggregation"),
        (sql_dir / "08_agg_unit_performance.sql", "Unit performance aggregation"),
        (sql_dir / "09_agg_product_performance.sql", "Product performance aggregation"),
    ]

    # Execute transformations
    print("\n" + "="*60)
    print("Executing Aggregation Queries")
    print("="*60)

    success_count = 0
    for sql_file, description in sql_files:
        if execute_sql_file(client, sql_file, description):
            success_count += 1

    # Verify results
    if success_count == len(sql_files):
        verify_aggregations(client, args.project, args.dataset)
        show_sample_data(client, args.project, args.dataset)

        print("\n[SUCCESS] KPI aggregation tables built successfully!")
        print("\nNext: Create Looker Studio dashboards")
        print("      See docs/LOOKER_STUDIO_SETUP.md for instructions")
        return 0
    else:
        print(f"\n[ERROR] {len(sql_files) - success_count} aggregation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
