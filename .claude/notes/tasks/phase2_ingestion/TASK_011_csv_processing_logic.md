# TASK_011: CSV Processing Logic (pandas)

## Description

Document and refine the Python/pandas processing logic used inside the Cloud Function (TASK_010). This task focuses on the data transformation rules: schema enforcement, type casting, deduplication, validation, and enrichment. The processing logic replaces the original PySpark jobs from the strategic plan.

## Prerequisites

- TASK_010 complete (Cloud Function structure exists)

## Processing Rules

### Schema Enforcement

```python
# pedido.csv -- Expected columns and types
PEDIDO_SCHEMA = {
    "Id_Unidade": "int64",
    "Id_Pedido": "string",
    "Tipo_Pedido": "string",       # "Loja Online" or "Loja Fisica"
    "Data_Pedido": "date",          # YYYY-MM-DD
    "Vlr_Pedido": "float64",       # Decimal(10,2)
    "Endereco_Entrega": "string",  # Nullable
    "Taxa_Entrega": "float64",     # Decimal(10,2)
    "Status": "string",            # "Finalizado", "Pendente", "Cancelado"
}

# item_pedido.csv -- Expected columns and types
ITEM_PEDIDO_SCHEMA = {
    "Id_Pedido": "string",
    "Id_Item_Pedido": "string",
    "Id_Produto": "int64",
    "Qtd": "int64",
    "Vlr_Item": "float64",        # Decimal(10,2)
    "Observacao": "string",        # Nullable
}
```

### Validation Rules

```python
def apply_validation_rules(df: pd.DataFrame, file_type: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply validation rules. Returns (valid_df, rejected_df).
    """
    valid = df.copy()
    rejected_records = []

    if file_type == "pedido":
        # Rule 1: Id_Unidade must be positive integer
        mask = valid["Id_Unidade"] <= 0
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Id_Unidade <= 0"))
            valid = valid[~mask]

        # Rule 2: Id_Pedido must not be empty
        mask = valid["Id_Pedido"].isna() | (valid["Id_Pedido"] == "")
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Empty Id_Pedido"))
            valid = valid[~mask]

        # Rule 3: Status must be valid
        mask = ~valid["Status"].isin(["Finalizado", "Pendente", "Cancelado"])
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Invalid Status"))
            valid = valid[~mask]

        # Rule 4: Vlr_Pedido must be positive
        mask = valid["Vlr_Pedido"] <= 0
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Vlr_Pedido <= 0"))
            valid = valid[~mask]

        # Rule 5: Data_Pedido must be valid date (not future)
        today = pd.Timestamp.now().normalize()
        mask = pd.to_datetime(valid["Data_Pedido"], errors="coerce") > today
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Future date"))
            valid = valid[~mask]

        # Rule 6: Tipo_Pedido must be valid
        mask = ~valid["Tipo_Pedido"].isin(["Loja Online", "Loja Fisica"])
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Invalid Tipo_Pedido"))
            valid = valid[~mask]

        # Rule 7: Online orders should have delivery address
        # (warning only, not rejection)

    elif file_type == "item_pedido":
        # Rule 1: Id_Produto must be positive
        mask = valid["Id_Produto"] <= 0
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Id_Produto <= 0"))
            valid = valid[~mask]

        # Rule 2: Qtd must be positive
        mask = valid["Qtd"] <= 0
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Qtd <= 0"))
            valid = valid[~mask]

        # Rule 3: Vlr_Item must be positive
        mask = valid["Vlr_Item"] <= 0
        if mask.any():
            rejected_records.append(valid[mask].assign(_rejection_reason="Vlr_Item <= 0"))
            valid = valid[~mask]

    rejected = pd.concat(rejected_records) if rejected_records else pd.DataFrame()
    return valid, rejected
```

### Deduplication Logic

```python
def deduplicate(df: pd.DataFrame, file_type: str) -> pd.DataFrame:
    """
    Remove duplicate records based on primary key.
    Keeps the LAST occurrence (latest in file order).
    """
    if file_type == "pedido":
        pk = "Id_Pedido"
    elif file_type == "item_pedido":
        pk = "Id_Item_Pedido"
    else:
        return df

    before = len(df)
    df = df.drop_duplicates(subset=[pk], keep="last")
    after = len(df)

    if before != after:
        print(f"  [DEDUP] Removed {before - after} duplicates on {pk}")

    return df
```

### Metadata Enrichment

```python
def enrich_metadata(df: pd.DataFrame, source_file: str) -> pd.DataFrame:
    """Add lineage and processing metadata columns."""
    df["_source_file"] = source_file
    df["_ingest_timestamp"] = pd.Timestamp.now(tz="UTC")
    df["_ingest_date"] = pd.Timestamp.now().date()
    return df
```

### Full Processing Pipeline

```python
def process_pedido(df_raw: pd.DataFrame, source_file: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Full processing pipeline for pedido.csv."""
    # 1. Schema enforcement
    df = enforce_schema(df_raw, "pedido")

    # 2. Type casting
    df["Id_Unidade"] = pd.to_numeric(df["Id_Unidade"], errors="coerce").astype("Int64")
    df["Vlr_Pedido"] = pd.to_numeric(df["Vlr_Pedido"], errors="coerce")
    df["Taxa_Entrega"] = pd.to_numeric(df["Taxa_Entrega"], errors="coerce").fillna(0.0)
    df["Data_Pedido"] = pd.to_datetime(df["Data_Pedido"], errors="coerce")

    # 3. Validation
    df_valid, df_rejected = apply_validation_rules(df, "pedido")

    # 4. Deduplication
    df_valid = deduplicate(df_valid, "pedido")

    # 5. Metadata enrichment
    df_valid = enrich_metadata(df_valid, source_file)

    return df_valid, df_rejected
```

## Acceptance Criteria

- [ ] Schema enforcement catches missing columns
- [ ] Type casting handles malformed values gracefully (coerce to NaN)
- [ ] Validation rules reject invalid records (not valid statuses, negative values, etc.)
- [ ] Deduplication removes duplicates by primary key
- [ ] Metadata columns (_source_file, _ingest_timestamp, _ingest_date) are added
- [ ] Rejected records are captured separately for quarantine

## Cost Impact

| Action | Cost |
|--------|------|
| Code development | Free (local) |
| **Total** | **$0.00** |

---

*TASK_011 of 26 -- Phase 2: Ingestion*
