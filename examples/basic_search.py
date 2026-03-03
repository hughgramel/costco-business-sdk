"""Basic product search example."""

from costco_business_sdk import CostcoBusiness

client = CostcoBusiness(location="115")  # Lynnwood, WA

# Search for coffee products
products = client.search("coffee", limit=10)

print(f"Found {len(products)} coffee products:\n")
for p in products:
    price = f"${p.list_price:.2f}"
    sale = f" (SALE ${p.sale_price:.2f}, {p.discount_pct}% off)" if p.on_sale else ""
    print(f"  [{p.item_number}] {p.name}")
    print(f"    {price}{sale} — {p.stock_status}")
    print()

client.close()
