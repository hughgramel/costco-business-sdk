# costco-business-sdk

Python SDK for the Costco Business Delivery product search API — search products, check prices, find deals, and browse categories across all US Business Center locations.

## Features

- **Product Search** — Search 2,500+ products per location by keyword with real-time pricing and stock status
- **Deal Finder** — Find discounted items filtered by minimum discount percentage
- **Location Discovery** — Find the nearest Business Center to any US zip code
- **Category Browser** — Explore the full product category hierarchy
- **Full Catalog Export** — Dump entire product catalogs to CSV or JSON
- **CLI Tool** — `costco-biz` command-line interface for all operations
- **Rate Limiting** — Built-in request throttling with configurable delay
- **Retry Logic** — Automatic retries with exponential backoff on transient errors

## Installation

```bash
pip install costco-business-sdk
```

Or install from source:

```bash
git clone https://github.com/hughgramel/costco-business-sdk.git
cd costco-business-sdk
pip install -e .
```

For development (includes pytest, ruff):

```bash
pip install -e ".[dev]"
```

## Quick Start

### Python Library

```python
from costco_business_sdk import CostcoBusiness

client = CostcoBusiness()

# Find your nearest Business Center
nearby = client.find_nearest("98105")
print(nearby[0])  # Location(id='115', name='Lynnwood Bus Ctr', distance_mi=11.4, ...)

# Search products at that location
products = client.search("coffee", location="115", limit=10)
for p in products:
    print(f"{p.name}: ${p.list_price}")

# Find deals (20%+ off)
deals = client.deals(location="115", min_discount=20)
for d in deals:
    print(f"{d.discount_pct}% off: {d.name} (${d.sale_price})")

# Browse categories
categories = client.categories()
for cat in categories:
    print(f"{cat.name} ({cat.count} products)")

# Full catalog export
all_products = client.dump(location="115")

client.close()
```

### Context Manager

```python
from costco_business_sdk import CostcoBusiness

with CostcoBusiness(location="115") as client:
    products = client.search("paper towels")
    count = client.count()
    print(f"Location 115 has {count:,} total products")
```

### Export to Files

```python
from costco_business_sdk import CostcoBusiness
from costco_business_sdk.exporters import to_csv, to_json

with CostcoBusiness(location="115") as client:
    products = client.search("water", limit=50)

    to_csv(products, "water_products.csv")
    to_json(products, "water_products.json")
```

### CLI

```bash
# Find nearest Business Center
costco-biz nearest 98105

# Search products
costco-biz search "coffee" --location 115

# Search with limit and export
costco-biz search "coffee" -l 115 -n 50 -f csv -o coffee.csv

# Find deals (20%+ off)
costco-biz deals --location 115 --min-discount 20

# Browse categories
costco-biz categories

# Export full catalog to CSV
costco-biz dump --location 115 --format csv --output ./data/

# Export full catalog to JSON
costco-biz dump --location 115 --format json --output ./data/

# List all Business Center locations
costco-biz locations

# Count products at a location
costco-biz count --location 115

# Count products matching a query
costco-biz count "organic" --location 115
```

## API Reference

### `CostcoBusiness(location=None, api_key=None, delay=1.0)`

Main client class. All methods are available on this object.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location` | `str` | `"888"` | Default warehouse ID for all queries |
| `api_key` | `str` | `None` | Override API key (or set `COSTCO_API_KEY` env var) |
| `delay` | `float` | `1.0` | Seconds between API requests |

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `search(query, location, limit)` | Search products by keyword | `list[Product]` |
| `deals(location, min_discount)` | Find products on sale | `list[Product]` |
| `count(query, location)` | Count matching products | `int` |
| `dump(location)` | Fetch full catalog (all products) | `list[Product]` |
| `categories(location)` | Browse category hierarchy | `list[Category]` |
| `find_nearest(zip_code, limit)` | Find nearest Business Centers | `list[Location]` |
| `locations()` | List all known Business Centers | `list[Location]` |
| `location_info(warehouse_id)` | Get info for a specific location | `Location` |
| `close()` | Close the HTTP client | `None` |

### Data Models

#### `Product`

Each product includes 40+ fields parsed from the API response:

| Category | Fields |
|----------|--------|
| **Identity** | `item_number`, `name`, `description`, `group_id`, `brand`, `upc` |
| **Physical** | `case_count`, `container_size` |
| **Pricing** | `list_price`, `sale_price`, `discount_pct`, `on_sale`, `currency` |
| **Stock** | `stock_status`, `availability`, `warehouse_id` |
| **Classification** | `category_path`, `department`, `category_code`, `item_class` |
| **Attributes** | `buyable`, `member_only`, `fsa_eligible`, `variable_weight`, `dietary_features` |
| **Media** | `image_url`, `marketing_statement`, `marketing_features` |
| **Ratings** | `rating`, `review_count` |

#### `Location`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Warehouse ID (e.g., `"115"`) |
| `name` | `str` | Business Center name |
| `city` | `str` | City |
| `state` | `str` | State abbreviation |
| `zip_code` | `str` | Zip code |
| `latitude` | `float` | Latitude |
| `longitude` | `float` | Longitude |
| `distance_mi` | `float` | Distance in miles (set by `find_nearest()`) |

#### `Category`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Category name |
| `url` | `str` | Category URL path |
| `count` | `int` | Number of products |
| `children` | `list[Category]` | Subcategories |

## Business Center Locations

The SDK includes a registry of all 30 known Costco Business Center locations:

| ID | Name | City | State |
|----|------|------|-------|
| 10 | Hackensack Bus Ctr | Hackensack | NJ |
| 63 | NE Anchorage | Anchorage | AK |
| 113 | Salt Lake City Bus Ctr | Salt Lake City | UT |
| 115 | Lynnwood Bus Ctr | Lynnwood | WA |
| 563 | Las Vegas Bus Ctr | Las Vegas | NV |
| 564 | Hawthorne Bus Ctr | Hawthorne | CA |
| 569 | Commerce Bus Ctr | Commerce | CA |
| 578 | San Diego Bus Ctr | San Diego | CA |
| 579 | Morrow Bus Ctr | Morrow | GA |
| 580 | Bedford Park Bus Ctr | Chicago | IL |
| 650 | Denver Bus Ctr | Denver | CO |
| 651 | Orlando Bus Ctr | Orlando | FL |
| 652 | Minneapolis Bus Ctr | Minneapolis | MN |
| 653 | Burbank Bus Ctr | North Hollywood | CA |
| 654 | S San Francisco Bus Ctr | South San Francisco | CA |
| 655 | Dallas Bus Ctr | Dallas | TX |
| 729 | Hackensack Bus Ctr | Hackensack | NJ |
| 767 | Fife Bus Ctr | Fife | WA |
| 823 | Hayward Bus Ctr | Hayward | CA |
| 827 | Phoenix Bus Ctr | Phoenix | AZ |
| 848 | San Jose Bus Ctr | San Jose | CA |
| 893 | Sacramento Bus Ctr | Sacramento | CA |
| 943 | Westminster Bus Ctr | Westminster | CA |
| 947 | Ontario Bus Ctr | Ontario | CA |
| 1487 | Stafford Bus Ctr | Stafford | TX |
| 1581 | San Marcos Bus Ctr | San Marcos | CA |
| 1661 | Anchorage Bus Ctr | Anchorage | AK |
| 1663 | Southfield Bus Ctr | Southfield | MI |
| 1665 | St. Louis Bus Ctr | St. Louis | MO |

Use `costco-biz locations` or `client.locations()` to see the full list. Use `costco-biz nearest <zip>` or `client.find_nearest("<zip>")` to find the closest one to you.

## How It Works

Costco Business Delivery uses a [Solr/Fusion](https://lucidworks.com/) search engine to power product search on [costcobusinessdelivery.com](https://www.costcobusinessdelivery.com). The API key is publicly embedded in the site's frontend JavaScript — it's the same key every visitor's browser uses to load product data.

This SDK calls that same search API directly via HTTP, returning structured product data with real pricing, stock status, discounts, and more. No browser automation, no login, no HTML scraping — just clean JSON responses from a public API.

### Architecture

```
costco-business-sdk/
├── src/costco_business_sdk/
│   ├── __init__.py      # Public API exports
│   ├── client.py        # CostcoBusiness class — main interface
│   ├── http.py          # HTTP transport, pagination, rate limiting, retries
│   ├── models.py        # Product, Category, Location dataclasses
│   ├── locations.py     # Business Center registry + find_nearest()
│   ├── exporters.py     # CSV, JSON, Rich table output
│   └── cli.py           # Typer CLI (costco-biz command)
├── tests/               # Unit tests with offline fixtures
└── examples/            # Runnable example scripts
```

### APIs Used

| API | Purpose |
|-----|---------|
| **Product Search** (`search.costcobusinessdelivery.com`) | Search products, get pricing/stock by location |
| **Megamenu** (`search.costcobusinessdelivery.com`) | Category hierarchy |
| **Geocode** (`geocodeservice.costco.com`) | Convert zip codes to coordinates |

### Price Variation by Location

Prices and stock status vary by warehouse location. Always pass a `location` parameter to get accurate local pricing. Without a location, the API returns national-level data (location `888`) which may differ from your local store.

**Tip:** You can see your currently active location in the footer of [costcobusinessdelivery.com](https://www.costcobusinessdelivery.com).

## Configuration

### API Key

The SDK uses a default API key embedded in Costco's frontend JavaScript. If Costco rotates it, you can provide a new one without waiting for a SDK update:

```python
# Via constructor
client = CostcoBusiness(api_key="your-key-here")
```

```bash
# Via environment variable
export COSTCO_API_KEY="your-key-here"
```

### Rate Limiting

The SDK waits 1 second between API requests by default to be respectful of the API:

```python
client = CostcoBusiness(delay=0.5)  # Faster
client = CostcoBusiness(delay=2.0)  # More conservative
```

### Error Handling

The SDK raises specific exceptions you can catch:

```python
from costco_business_sdk import CostcoBusiness, CostcoAPIError, RateLimitError

try:
    client = CostcoBusiness(location="115")
    products = client.search("coffee")
except RateLimitError:
    print("Rate limited — try increasing the delay parameter")
except CostcoAPIError as e:
    print(f"API error: {e}")
```

## Examples

See the [`examples/`](examples/) directory for runnable scripts:

- [`basic_search.py`](examples/basic_search.py) — Search products by keyword
- [`find_deals.py`](examples/find_deals.py) — Find items with 20%+ discount
- [`nearest_location.py`](examples/nearest_location.py) — Find the closest Business Center to a zip code

## Development

```bash
git clone https://github.com/hughgramel/costco-business-sdk.git
cd costco-business-sdk
pip install -e ".[dev]"
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_models.py
```

Tests use offline fixtures (saved API responses in `tests/fixtures/`) and don't make any real API calls.

## Legal Note

This SDK accesses publicly available data through the same API that powers the Costco Business Delivery website. No authentication bypass, credential harvesting, or terms-of-service circumvention is involved. The API key is publicly embedded in the website's JavaScript source code and is not a secret credential — every visitor's browser uses it.

Use this tool responsibly. This project is not affiliated with, endorsed by, or connected to Costco Wholesale Corporation.

## License

MIT
