# costco-business-sdk

Python SDK for the Costco Business Delivery product search API — search products, check prices, find deals, and browse categories across all US Business Center locations.

## What This Does

Costco Business Centers (~27 locations across the US) sell bulk products to businesses and individuals. Their product catalog — including real-time pricing, stock status, and discounts — is available through a public search API that powers their website.

This SDK provides a clean Python interface and command-line tool to access that catalog data.

## Installation

```bash
pip install costco-business-sdk
```

## Quick Start

### Python Library

```python
from costco_business_sdk import CostcoBusiness

client = CostcoBusiness()

# Find your nearest Business Center
nearby = client.find_nearest("98105")
print(nearby[0])  # Location(id='115', name='Lynnwood Bus Ctr', distance_mi=8.2, ...)

# Search products at that location
products = client.search("coffee", location="115")
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
```

### CLI

```bash
# Find nearest Business Center
costco-biz nearest 98105

# Search products
costco-biz search "coffee" --location 115

# Find deals
costco-biz deals --location 115 --min-discount 20

# Browse categories
costco-biz categories

# Export full catalog
costco-biz dump --location 115 --format csv --output ./data/

# List all Business Center locations
costco-biz locations

# Count products
costco-biz count --location 115
```

## How It Works

Costco Business Delivery uses a [Solr/Fusion](https://lucidworks.com/) search engine to power product search on [costcobusinessdelivery.com](https://www.costcobusinessdelivery.com). The API key is publicly embedded in the site's frontend JavaScript — it's how every visitor's browser loads product data.

This SDK calls that same search API directly via HTTP, returning structured product data with real pricing, stock status, discounts, and more. No browser automation, no login, no HTML scraping — just clean JSON responses from a public API.

Prices and stock status vary by warehouse location. Pass a `location` parameter to get real local pricing for a specific Business Center.

**Tip:** You can see your currently active location in the footer of [costcobusinessdelivery.com](https://www.costcobusinessdelivery.com).

## Data Fields

Each product includes 40+ fields:

| Category | Fields |
|----------|--------|
| **Identity** | item_number, name, description, group_id, brand, upc |
| **Physical** | case_count, container_size |
| **Pricing** | list_price, sale_price, discount_pct, on_sale, currency |
| **Stock** | stock_status, availability, warehouse_id |
| **Classification** | category_path, department, category_code, item_class |
| **Attributes** | buyable, member_only, fsa_eligible, variable_weight, dietary_features |
| **Media** | image_url, marketing_statement, marketing_features |
| **Ratings** | rating, review_count |

## Configuration

### API Key

The SDK uses a default API key embedded in Costco's frontend JavaScript. If Costco rotates it, you can provide a new one:

```python
# Via constructor
client = CostcoBusiness(api_key="your-key-here")

# Via environment variable
export COSTCO_API_KEY="your-key-here"
```

### Rate Limiting

The SDK waits 1 second between API requests by default. This is configurable:

```python
client = CostcoBusiness(delay=0.5)  # Faster, but be respectful
```

## Legal Note

This SDK accesses publicly available data through the same API that powers the Costco Business Delivery website. No authentication bypass, credential harvesting, or terms-of-service circumvention is involved. The API key is publicly embedded in the website's JavaScript source code and is not a secret credential.

Use this tool responsibly.

## License

MIT
