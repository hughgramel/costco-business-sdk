"""Tests for data models."""

from costco_business_sdk.models import Category, Location, Product


def test_product_from_api_doc(search_response):
    """Product.from_api_doc correctly parses a raw API document."""
    docs = search_response["response"]["docs"]
    product = Product.from_api_doc(docs[0], warehouse_id="115")

    assert product.item_number != ""
    assert product.name != ""
    assert product.warehouse_id == "115"
    assert isinstance(product.list_price, float)
    assert isinstance(product.on_sale, bool)


def test_product_discount_calculation():
    """Discount is calculated correctly when on sale."""
    doc = {
        "item_number": "12345",
        "name": "Test Product",
        "item_location_pricing_listPrice": 100.0,
        "item_location_pricing_salePrice": 80.0,
    }
    product = Product.from_api_doc(doc, warehouse_id="115")

    assert product.on_sale is True
    assert product.discount_pct == 20.0
    assert product.list_price == 100.0
    assert product.sale_price == 80.0


def test_product_no_discount():
    """No discount when prices are the same."""
    doc = {
        "item_number": "12345",
        "name": "Test Product",
        "item_location_pricing_listPrice": 50.0,
        "item_location_pricing_salePrice": 50.0,
    }
    product = Product.from_api_doc(doc, warehouse_id="115")

    assert product.on_sale is False
    assert product.discount_pct == 0.0


def test_product_to_dict():
    """to_dict produces a flat dictionary."""
    doc = {
        "item_number": "12345",
        "name": "Test Product",
        "Brand_attr": ["TestBrand"],
        "item_location_pricing_listPrice": 10.0,
    }
    product = Product.from_api_doc(doc, warehouse_id="115")
    d = product.to_dict()

    assert d["item_number"] == "12345"
    assert d["brand"] == "TestBrand"
    assert d["list_price"] == 10.0
    assert "warehouse_id" in d


def test_category_from_megamenu(megamenu_response):
    """Category tree is parsed from megamenu data."""
    nodes = megamenu_response["megaMenu"]
    categories = [Category.from_megamenu(n) for n in nodes]

    assert len(categories) > 0
    assert categories[0].name != ""


def test_location_from_warehouse_api():
    """Location is parsed from warehouse locator API data."""
    data = {
        "warehouse": {
            "warehouseId": "115",
            "name": [{"value": "Lynnwood Bus Ctr", "localeCode": "en-US"}],
            "address": {
                "line1": "19105 HIGHWAY 99",
                "city": "LYNNWOOD",
                "territory": "WA",
                "postalCode": "98036-5228",
                "latitude": 47.82565564,
                "longitude": -122.3104726,
            },
            "phone": "(425) 640-7700",
            "timeZone": "America/Los_Angeles",
            "hours": [],
            "services": [],
        }
    }
    loc = Location.from_warehouse_api(data)

    assert loc.id == "115"
    assert loc.name == "Lynnwood Bus Ctr"
    assert loc.city == "LYNNWOOD"
    assert loc.state == "WA"
    assert loc.latitude == 47.82565564
