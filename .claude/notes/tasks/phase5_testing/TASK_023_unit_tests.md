# TASK_023: Unit Tests (Python)

## Description

Create unit tests for all Python scripts: fake data generator, CSV processing logic, and upload utilities. Tests use pytest and run locally without GCP dependencies (mocked).

## Prerequisites

- Python code from TASK_005, TASK_009, TASK_010, TASK_011 complete

## Test File

Create `tests/unit/test_generate_fake_sales.py`:

```python
"""Unit tests for the fake data generator."""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from generate_fake_sales import (
    generate_unit_list,
    generate_orders_for_unit_day,
    generate_reference_data,
    PRODUCT_CATALOG,
    STATES,
    COUNTRIES,
    STATUS_CHOICES,
    ORDER_TYPE_CHOICES,
)
from faker import Faker


class TestUnitList:
    def test_default_50_units(self):
        units = generate_unit_list(50)
        assert len(units) == 50

    def test_custom_unit_count(self):
        for count in [1, 5, 10, 100]:
            units = generate_unit_list(count)
            assert len(units) == count

    def test_unique_ids(self):
        units = generate_unit_list(50)
        ids = [u["id"] for u in units]
        assert len(set(ids)) == 50

    def test_all_units_have_state(self):
        units = generate_unit_list(50)
        for unit in units:
            assert unit["state_id"] in [1, 2, 3]

    def test_unit_name_format(self):
        units = generate_unit_list(5)
        for unit in units:
            assert unit["name"].startswith("Mr. Health")


class TestOrderGeneration:
    def setup_method(self):
        self.fake = Faker("pt_BR")
        self.fake.seed_instance(42)
        self.date = datetime(2026, 1, 15)

    def test_generates_correct_number_of_orders(self):
        orders, items = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=10, max_orders=10
        )
        assert len(orders) == 10

    def test_order_has_required_fields(self):
        orders, items = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=1, max_orders=1
        )
        required = ["Id_Unidade", "Id_Pedido", "Tipo_Pedido", "Data_Pedido",
                     "Vlr_Pedido", "Endereco_Entrega", "Taxa_Entrega", "Status"]
        for field in required:
            assert field in orders[0], f"Missing field: {field}"

    def test_item_has_required_fields(self):
        orders, items = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=1, max_orders=1
        )
        required = ["Id_Pedido", "Id_Item_Pedido", "Id_Produto", "Qtd", "Vlr_Item", "Observacao"]
        for field in required:
            assert field in items[0], f"Missing field: {field}"

    def test_order_references_correct_unit(self):
        orders, _ = generate_orders_for_unit_day(
            self.fake, unit_id=42, date=self.date, min_orders=5, max_orders=5
        )
        for order in orders:
            assert order["Id_Unidade"] == 42

    def test_items_reference_valid_orders(self):
        orders, items = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=5, max_orders=5
        )
        order_ids = {o["Id_Pedido"] for o in orders}
        for item in items:
            assert item["Id_Pedido"] in order_ids

    def test_valid_statuses(self):
        orders, _ = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=50, max_orders=50
        )
        for order in orders:
            assert order["Status"] in STATUS_CHOICES

    def test_valid_order_types(self):
        orders, _ = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=50, max_orders=50
        )
        for order in orders:
            assert order["Tipo_Pedido"] in ORDER_TYPE_CHOICES

    def test_physical_orders_no_delivery_fee(self):
        """Physical orders should have 0.00 delivery fee."""
        orders, _ = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=100, max_orders=100
        )
        physical = [o for o in orders if o["Tipo_Pedido"] == "Loja Fisica"]
        for order in physical:
            assert float(order["Taxa_Entrega"]) == 0.00

    def test_product_ids_in_catalog(self):
        _, items = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=20, max_orders=20
        )
        valid_ids = {p["id"] for p in PRODUCT_CATALOG}
        for item in items:
            assert item["Id_Produto"] in valid_ids

    def test_positive_quantities(self):
        _, items = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=20, max_orders=20
        )
        for item in items:
            assert item["Qtd"] >= 1

    def test_date_format(self):
        orders, _ = generate_orders_for_unit_day(
            self.fake, unit_id=1, date=self.date, min_orders=1, max_orders=1
        )
        assert orders[0]["Data_Pedido"] == "2026-01-15"


class TestReferenceData:
    def test_product_catalog_has_30_items(self):
        assert len(PRODUCT_CATALOG) == 30

    def test_states_are_southern_brazil(self):
        state_names = {s["name"] for s in STATES}
        assert "Rio Grande do Sul" in state_names
        assert "Santa Catarina" in state_names
        assert "Parana" in state_names

    def test_countries_has_brazil(self):
        assert len(COUNTRIES) == 1
        assert COUNTRIES[0]["name"] == "Brasil"

    def test_reference_data_generates_csvs(self, tmp_path):
        units = generate_unit_list(5)
        generate_reference_data(units, tmp_path)

        assert (tmp_path / "reference_data" / "produto.csv").exists()
        assert (tmp_path / "reference_data" / "unidade.csv").exists()
        assert (tmp_path / "reference_data" / "estado.csv").exists()
        assert (tmp_path / "reference_data" / "pais.csv").exists()

    def test_produto_csv_has_correct_columns(self, tmp_path):
        units = generate_unit_list(5)
        generate_reference_data(units, tmp_path)
        df = pd.read_csv(tmp_path / "reference_data" / "produto.csv", sep=";")
        assert "Id_Produto" in df.columns
        assert "Nome_Produto" in df.columns
        assert len(df) == 30


class TestReproducibility:
    def test_seed_produces_same_output(self):
        """Same seed should produce identical data."""
        import random
        random.seed(42)
        Faker.seed(42)
        fake1 = Faker("pt_BR")
        fake1.seed_instance(42)
        orders1, _ = generate_orders_for_unit_day(fake1, 1, datetime(2026, 1, 1), 10, 10)

        random.seed(42)
        Faker.seed(42)
        fake2 = Faker("pt_BR")
        fake2.seed_instance(42)
        orders2, _ = generate_orders_for_unit_day(fake2, 1, datetime(2026, 1, 1), 10, 10)

        assert len(orders1) == len(orders2)
        for o1, o2 in zip(orders1, orders2):
            assert o1["Id_Pedido"] == o2["Id_Pedido"]
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ -v --cov=scripts --cov-report=term-missing

# Run specific test class
pytest tests/unit/test_generate_fake_sales.py::TestOrderGeneration -v
```

## Acceptance Criteria

- [ ] All unit tests pass: `pytest tests/unit/ -v`
- [ ] Coverage > 80% for generate_fake_sales.py
- [ ] Tests run without any GCP dependencies (fully local)
- [ ] Tests complete in under 30 seconds

## Cost Impact

| Action | Cost |
|--------|------|
| Local test execution | Free |
| **Total** | **$0.00** |

---

*TASK_023 of 26 -- Phase 5: Testing*
