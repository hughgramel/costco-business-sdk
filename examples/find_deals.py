"""Find the best deals at a Business Center."""

from costco_business_sdk import CostcoBusiness

client = CostcoBusiness(location="115")

# Find items with 20%+ discount
deals = client.deals(min_discount=20)

print(f"Found {len(deals)} items with 20%+ discount:\n")
for d in deals[:20]:
    print(f"  {d.discount_pct}% off: {d.name[:60]}")
    print(f"    Was ${d.list_price:.2f} → Now ${d.sale_price:.2f}")
    print()

client.close()
