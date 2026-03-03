"""Tests for export functionality."""

import csv
import json
from pathlib import Path

from costco_business_sdk.exporters import to_csv, to_json, to_table
from costco_business_sdk.models import Product


def _make_product(**overrides) -> Product:
    """Create a test product with defaults."""
    doc = {
        "item_number": "12345",
        "name": "Test Product",
        "Brand_attr": ["TestBrand"],
        "item_location_pricing_listPrice": 29.99,
        "item_location_pricing_salePrice": 24.99,
        "item_location_stockStatus": "in stock",
    }
    doc.update(overrides)
    return Product.from_api_doc(doc, warehouse_id="115")


def test_to_csv(tmp_path):
    """CSV export produces a valid file with headers and data."""
    products = [_make_product(), _make_product(item_number="67890", name="Other Product")]
    path = to_csv(products, tmp_path / "test.csv")

    assert path.exists()
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["item_number"] == "12345"
    assert "fetched_at" in rows[0]


def test_to_json(tmp_path):
    """JSON export produces valid JSON with metadata."""
    products = [_make_product()]
    path = to_json(products, tmp_path / "test.json")

    assert path.exists()
    data = json.loads(path.read_text())

    assert "fetched_at" in data
    assert data["count"] == 1
    assert len(data["products"]) == 1
    assert data["products"][0]["item_number"] == "12345"


def test_to_table():
    """Rich table is created with correct columns."""
    products = [_make_product()]
    table = to_table(products)

    assert table.row_count == 1
