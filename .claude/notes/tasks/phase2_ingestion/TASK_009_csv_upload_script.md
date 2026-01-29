# TASK_009: CSV Upload Script

## Description

Create a Python script that uploads generated CSV sales files to GCS, simulating the daily upload that each unit would perform at midnight. The script uploads files from the local output directory to the GCS raw/csv_sales/ prefix, preserving the date and unit directory structure.

## Prerequisites

- TASK_003 complete (GCS bucket exists)
- TASK_005 complete (fake data generated in output/csv_sales/)

## Steps

### Step 1: Create Upload Script

Create `scripts/upload_to_gcs.py`:

```python
#!/usr/bin/env python3
"""
Upload CSV sales files to GCS, simulating unit daily uploads.

Usage:
    # Upload all generated data
    python upload_to_gcs.py --source-dir ./output/csv_sales

    # Upload a specific date
    python upload_to_gcs.py --source-dir ./output/csv_sales --date 2026-01-28

    # Upload specific unit for a date
    python upload_to_gcs.py --source-dir ./output/csv_sales --date 2026-01-28 --unit 1
"""

import argparse
import os
from pathlib import Path
from google.cloud import storage


PROJECT = "case_ficticio-data-mvp"
BUCKET = "case_ficticio-data-lake-mvp"
GCS_PREFIX = "raw/csv_sales"


def upload_files(source_dir: Path, bucket_name: str, date_filter: str = None,
                 unit_filter: int = None) -> dict:
    """Upload CSV files to GCS preserving directory structure."""
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(bucket_name)

    stats = {"files_uploaded": 0, "bytes_uploaded": 0, "errors": 0}

    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if not filename.endswith(".csv"):
                continue

            local_path = Path(root) / filename
            # Build relative path: YYYY/MM/DD/unit_NNN/filename.csv
            rel_path = local_path.relative_to(source_dir)

            # Apply filters
            parts = str(rel_path).replace("\\", "/").split("/")
            if len(parts) >= 4:
                file_date = f"{parts[0]}-{parts[1]}-{parts[2]}"
                file_unit = parts[3]

                if date_filter and file_date != date_filter:
                    continue
                if unit_filter and file_unit != f"unit_{unit_filter:03d}":
                    continue

            gcs_path = f"{GCS_PREFIX}/{rel_path}".replace("\\", "/")

            try:
                blob = bucket.blob(gcs_path)
                blob.upload_from_filename(str(local_path))
                file_size = local_path.stat().st_size
                stats["files_uploaded"] += 1
                stats["bytes_uploaded"] += file_size
            except Exception as e:
                print(f"  [ERROR] Failed to upload {rel_path}: {e}")
                stats["errors"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(description="Upload CSV sales files to GCS")
    parser.add_argument("--source-dir", type=str, default="./output/csv_sales")
    parser.add_argument("--date", type=str, default=None,
                        help="Filter by date (YYYY-MM-DD)")
    parser.add_argument("--unit", type=int, default=None,
                        help="Filter by unit number")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be uploaded without uploading")
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        print("Run generate_fake_sales.py first.")
        return

    print(f"Uploading CSVs to gs://{BUCKET}/{GCS_PREFIX}/")
    if args.date:
        print(f"  Date filter: {args.date}")
    if args.unit:
        print(f"  Unit filter: unit_{args.unit:03d}")

    if args.dry_run:
        print("\n[DRY RUN] Counting files...")
        count = 0
        for root, dirs, files in os.walk(source_dir):
            count += len([f for f in files if f.endswith(".csv")])
        print(f"  Would upload {count} CSV files")
        return

    stats = upload_files(source_dir, BUCKET, args.date, args.unit)

    size_mb = stats["bytes_uploaded"] / (1024 * 1024)
    print(f"\nUpload complete:")
    print(f"  Files uploaded: {stats['files_uploaded']}")
    print(f"  Total size:     {size_mb:.2f} MB")
    print(f"  Errors:         {stats['errors']}")


if __name__ == "__main__":
    main()
```

### Step 2: Test Upload

```bash
# Dry run first
python scripts/upload_to_gcs.py --source-dir ./output/csv_sales --dry-run

# Upload one day for one unit (minimal test)
python scripts/upload_to_gcs.py --source-dir ./output/csv_sales --date 2026-01-28 --unit 1

# Upload one full day
python scripts/upload_to_gcs.py --source-dir ./output/csv_sales --date 2026-01-28

# Upload everything
python scripts/upload_to_gcs.py --source-dir ./output/csv_sales
```

### Step 3: Verify in GCS

```bash
# List uploaded files for a specific date/unit
gsutil ls gs://case_ficticio-data-lake-mvp/raw/csv_sales/2026/01/28/unit_001/
# Expected: pedido.csv, item_pedido.csv

# Count total files
gsutil ls -r gs://case_ficticio-data-lake-mvp/raw/csv_sales/ | wc -l

# Check total size
gsutil du -s gs://case_ficticio-data-lake-mvp/raw/csv_sales/
```

## Acceptance Criteria

- [ ] Script uploads CSVs to correct GCS path preserving directory structure
- [ ] Date filter works correctly
- [ ] Unit filter works correctly
- [ ] Dry-run mode works without uploading
- [ ] Verification shows files in GCS with correct structure

## Cost Impact

| Action | Cost |
|--------|------|
| GCS upload operations | Free (Class A ops within free tier) |
| GCS storage (~50 MB) | Free (within 5 GB) |
| **Total** | **$0.00** |

---

*TASK_009 of 26 -- Phase 2: Ingestion*
