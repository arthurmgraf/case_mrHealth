"""
Centralized Config Loader
===========================
Loads project_config.yaml with lru_cache for performance.
Used by all DAGs and operators to access project configuration.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

CONFIG_PATH = Path(
    os.environ.get("MRHEALTH_CONFIG_PATH", "/opt/airflow/config/project_config.yaml")
)

SQL_BASE = Path(
    os.environ.get("MRHEALTH_SQL_PATH", "/opt/airflow/sql")
)


@lru_cache(maxsize=1)
def load_config() -> dict[str, Any]:
    """Load and cache project configuration."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def get_project_id() -> str:
    config = load_config()
    project_id = config["project"]["id"]
    if project_id.startswith("${"):
        return os.environ.get("GCP_PROJECT_ID", "")
    return project_id


def get_sql_path(layer: str, filename: str) -> Path:
    return SQL_BASE / layer / filename
