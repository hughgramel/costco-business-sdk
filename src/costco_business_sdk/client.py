"""Main SDK client for Costco Business Delivery."""

from __future__ import annotations

from .http import HttpTransport
from .locations import BUSINESS_CENTERS, find_nearest_by_coords, get_all_locations
from .models import Category, Location, Product


class CostcoBusiness:
    """Python SDK for the Costco Business Delivery product search API.

    Args:
        location: Default warehouse location ID for queries. Use ``find_nearest()``
            to discover the closest Business Center to a zip code.
        api_key: Override the default API key. Can also be set via the
            ``COSTCO_API_KEY`` environment variable.
        delay: Seconds to wait between API requests (default 1.0).
    """

    def __init__(
        self,
        location: str | None = None,
        api_key: str | None = None,
        delay: float = 1.0,
    ):
        self._default_location = location or "888"
        self._http = HttpTransport(api_key=api_key, delay=delay)
        self._geocode_cache: dict[str, tuple[float, float]] = {}

    def _resolve_location(self, location: str | None) -> str:
        return location or self._default_location

    # ── Product search ──────────────────────────────────────────────

    def search(
        self,
        query: str = "*",
        location: str | None = None,
        limit: int | None = None,
    ) -> list[Product]:
        """Search for products by keyword.

        Args:
            query: Search query (supports Solr query syntax). Use ``"*"`` for all.
            location: Warehouse ID. Defaults to the client's default location.
            limit: Maximum number of products to return. ``None`` for all.

        Returns:
            List of matching products with pricing for the given location.
        """
        loc = self._resolve_location(location)
        products: list[Product] = []

        for doc in self._http.search_all(query=query, location=loc):
            products.append(Product.from_api_doc(doc, warehouse_id=loc))
            if limit and len(products) >= limit:
                break

        return products

    def deals(
        self,
        location: str | None = None,
        min_discount: float = 0,
    ) -> list[Product]:
        """Find products currently on sale.

        Args:
            location: Warehouse ID.
            min_discount: Minimum discount percentage to include (e.g., 20 = 20% off).

        Returns:
            List of discounted products, sorted by discount percentage (largest first).
        """
        all_products = self.search("*", location=location)
        deals = [p for p in all_products if p.on_sale and p.discount_pct >= min_discount]
        deals.sort(key=lambda p: p.discount_pct, reverse=True)
        return deals

    def count(self, query: str = "*", location: str | None = None) -> int:
        """Count products matching a query."""
        return self._http.count(query=query, location=self._resolve_location(location))

    def dump(self, location: str | None = None) -> list[Product]:
        """Fetch the full product catalog for a location.

        This is equivalent to ``search("*")`` — returns every product.
        """
        return self.search("*", location=location)

    # ── Categories ──────────────────────────────────────────────────

    def categories(self, location: str | None = None) -> list[Category]:
        """Fetch the category hierarchy.

        Returns:
            List of top-level categories, each with nested children.
        """
        loc = self._resolve_location(location)
        data = self._http.megamenu(location=loc)
        return [Category.from_megamenu(node) for node in data.get("megaMenu", [])]

    # ── Locations ───────────────────────────────────────────────────

    def find_nearest(self, zip_code: str, limit: int = 5) -> list[Location]:
        """Find the nearest Business Centers to a zip code.

        Uses Costco's geocode API to convert the zip code to coordinates,
        then calculates distance to all known Business Centers.

        Args:
            zip_code: US zip code (e.g., ``"98105"``).
            limit: Maximum number of locations to return.

        Returns:
            List of locations sorted by distance (nearest first).
        """
        lat, lon = self._geocode(zip_code)
        return find_nearest_by_coords(lat, lon, limit=limit)

    def locations(self) -> list[Location]:
        """List all known Costco Business Center locations."""
        return get_all_locations()

    def location_info(self, warehouse_id: str) -> Location | None:
        """Get info for a specific Business Center by warehouse ID."""
        info = BUSINESS_CENTERS.get(warehouse_id)
        if not info:
            return None
        return Location(
            id=warehouse_id,
            name=info["name"],
            address="",
            city=info["city"],
            state=info["state"],
            zip_code=info["zip"],
            latitude=info["lat"],
            longitude=info["lon"],
        )

    # ── Internal helpers ────────────────────────────────────────────

    def _geocode(self, zip_code: str) -> tuple[float, float]:
        """Convert a zip code to (latitude, longitude), with caching."""
        if zip_code in self._geocode_cache:
            return self._geocode_cache[zip_code]

        results = self._http.geocode(zip_code)
        if not results:
            raise ValueError(f"Could not geocode zip code: {zip_code}")

        lat = float(results[0].get("latitude", 0))
        lon = float(results[0].get("longitude", 0))
        self._geocode_cache[zip_code] = (lat, lon)
        return lat, lon

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> CostcoBusiness:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
