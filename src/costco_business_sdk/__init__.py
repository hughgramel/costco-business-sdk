"""Costco Business SDK — Python SDK for the Costco Business Delivery search API.

Search products, check prices, find deals, and browse categories across all
US Costco Business Center locations.

Example::

    from costco_business_sdk import CostcoBusiness

    client = CostcoBusiness(location="115")
    products = client.search("coffee")
    for p in products:
        print(f"{p.name}: ${p.list_price}")
"""

from .client import CostcoBusiness
from .http import CostcoAPIError, RateLimitError
from .models import Category, Location, Product

__all__ = [
    "CostcoBusiness",
    "CostcoAPIError",
    "Category",
    "Location",
    "Product",
    "RateLimitError",
]

__version__ = "0.1.0"
