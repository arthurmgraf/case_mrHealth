# TASK_005: Fake Data Generator (PRIORITY)

## Description

Create a Python script (`scripts/generate_fake_sales.py`) that generates realistic fake data for the Case Fictício - Teste data platform. This is the **highest priority technical task** because all subsequent phases depend on having test data. The script generates ORDER.CSV (pedido.csv) and ORDER_ITEM.CSV (item_pedido.csv) files matching the schema defined in `case_CaseFicticio.md`, plus static reference data CSVs for products, units, states, and countries.

## Prerequisites

- Python 3.9+ installed locally
- pip install faker pandas

## Requirements

### Functional Requirements
1. Generate `pedido.csv` and `item_pedido.csv` for configurable number of units (default: 50)
2. Generate reference data CSVs: `produto.csv`, `unidade.csv`, `estado.csv`, `pais.csv`
3. Configurable date range (default: last 30 days)
4. Configurable order volume per unit per day (default: 10-50 orders)
5. Realistic Brazilian addresses, product names, and unit names
6. Output structure matches the GCS prefix convention: `{output_dir}/{YYYY}/{MM}/{DD}/unit_{NNN}/`
7. Data volume stays within free tier limits (~500 MB total maximum)

### Data Schema Requirements

**pedido.csv columns:**
| Column | Type | Rules |
|--------|------|-------|
| Id_Unidade | INT | Matches unit ID |
| Id_Pedido | STRING | Unique UUID per order |
| Tipo_Pedido | STRING | "Loja Online" or "Loja Fisica" (60/40 split) |
| Data_Pedido | DATE | Within configured date range |
| Vlr_Pedido | DECIMAL(10,2) | Sum of items + delivery fee |
| Endereco_Entrega | STRING | Brazilian address (Faker pt_BR) |
| Taxa_Entrega | DECIMAL(10,2) | 0.00 for physical, 5.00-25.00 for online |
| Status | STRING | "Finalizado" (85%), "Pendente" (10%), "Cancelado" (5%) |

**item_pedido.csv columns:**
| Column | Type | Rules |
|--------|------|-------|
| Id_Pedido | STRING | FK to pedido.csv |
| Id_Item_Pedido | STRING | Unique UUID per item |
| Id_Produto | INT | Random from product catalog (1-30) |
| Qtd | INT | 1-5 |
| Vlr_Item | DECIMAL(10,2) | Matches product price |
| Observacao | STRING | Optional notes (30% chance of having one) |

### Reference Data
- **produto.csv**: 30 health food products with realistic names and prices
- **unidade.csv**: 50 units with names and state IDs (Southern Brazil: RS, SC, PR)
- **estado.csv**: Brazilian southern states
- **pais.csv**: Brazil

## Implementation

The full script is located at: `scripts/generate_fake_sales.py`

### Installation

```bash
pip install faker pandas
```

### Usage

```bash
# Generate default dataset (50 units, 30 days, 10-50 orders/unit/day)
python scripts/generate_fake_sales.py

# Generate smaller dataset for quick testing
python scripts/generate_fake_sales.py --units 5 --days 7 --min-orders 5 --max-orders 10

# Generate data for specific date range
python scripts/generate_fake_sales.py --start-date 2026-01-01 --end-date 2026-01-31

# Custom output directory
python scripts/generate_fake_sales.py --output-dir ./test_data
```

### Expected Output

```
output/
|-- reference_data/
|   |-- produto.csv          (~30 rows)
|   |-- unidade.csv          (~50 rows)
|   |-- estado.csv           (3 rows: RS, SC, PR)
|   |-- pais.csv             (1 row: Brasil)
|
|-- csv_sales/
|   |-- 2026/
|       |-- 01/
|           |-- 01/
|           |   |-- unit_001/
|           |   |   |-- pedido.csv
|           |   |   |-- item_pedido.csv
|           |   |-- unit_002/
|           |   |   |-- pedido.csv
|           |   |   |-- item_pedido.csv
|           |   |-- ...
|           |-- 02/
|           |-- ...
```

### Data Volume Estimation

| Config | Units | Days | Orders/Day | Total Orders | Total Items | CSV Size |
|--------|-------|------|------------|--------------|-------------|----------|
| Minimal | 5 | 7 | 10 | 350 | ~1,050 | ~500 KB |
| Default | 50 | 30 | 30 (avg) | 45,000 | ~135,000 | ~50 MB |
| Maximum | 50 | 90 | 50 | 225,000 | ~675,000 | ~250 MB |

All configurations stay well within the 5 GB GCS free tier.

## Acceptance Criteria

- [ ] Script runs without errors: `python scripts/generate_fake_sales.py --units 5 --days 3`
- [ ] pedido.csv has correct columns matching case_CaseFicticio.md schema
- [ ] item_pedido.csv has correct columns with valid FK to pedido.csv
- [ ] All reference CSVs generated (produto, unidade, estado, pais)
- [ ] Output directory structure matches GCS prefix convention
- [ ] Data types are correct (dates in ISO format, decimals with 2 places)
- [ ] Status distribution approximately matches: 85% Finalizado, 10% Pendente, 5% Cancelado
- [ ] Tipo_Pedido distribution approximately 60% Online / 40% Fisica
- [ ] Vlr_Pedido equals sum of (Qtd * Vlr_Item) + Taxa_Entrega
- [ ] Configurable via CLI arguments

## Verification Steps

```bash
# 1. Run the generator
python scripts/generate_fake_sales.py --units 3 --days 2

# 2. Check output structure
find output/ -type f -name "*.csv" | head -20

# 3. Validate pedido.csv headers
head -1 output/csv_sales/2026/01/28/unit_001/pedido.csv
# Expected: Id_Unidade;Id_Pedido;Tipo_Pedido;Data_Pedido;Vlr_Pedido;Endereco_Entrega;Taxa_Entrega;Status

# 4. Validate item_pedido.csv headers
head -1 output/csv_sales/2026/01/28/unit_001/item_pedido.csv
# Expected: Id_Pedido;Id_Item_Pedido;Id_Produto;Qtd;Vlr_Item;Observacao

# 5. Count records
wc -l output/csv_sales/2026/01/28/unit_001/pedido.csv

# 6. Check reference data
cat output/reference_data/estado.csv
cat output/reference_data/pais.csv
```

## Cost Impact

| Action | Cost |
|--------|------|
| Script development | Free (local execution) |
| Data generation | Free (local execution) |
| **Total** | **$0.00** |

---

*TASK_005 of 26 -- Phase 1: Foundation (CRITICAL PRIORITY)*
