"""Find the nearest Costco Business Center to a zip code."""

from costco_business_sdk import CostcoBusiness

client = CostcoBusiness()

zip_code = "98105"  # Seattle, WA
print(f"Nearest Business Centers to {zip_code}:\n")

locations = client.find_nearest(zip_code, limit=5)
for loc in locations:
    print(f"  #{loc.id} {loc.name}")
    print(f"    {loc.city}, {loc.state} {loc.zip_code}")
    print(f"    {loc.distance_mi:.1f} miles away")
    print()

client.close()
