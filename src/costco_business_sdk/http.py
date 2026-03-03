"""Low-level HTTP transport for Costco Business Delivery APIs."""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from typing import Any

import httpx

_VERSION = "0.1.0"

DEFAULT_API_KEY = "63b948d8-7d06-451b-acbe-f75815e96252"

SEARCH_URL = (
    "https://search.costcobusinessdelivery.com/api/apps/"
    "www_costcobusinessdelivery_com/query/www_costcobusinessdelivery_com_search"
)
MEGAMENU_URL = (
    "https://search.costcobusinessdelivery.com/api/apps/"
    "www_costcobusinessdelivery_com/query/www_costcobusinessdelivery_com_megamenu"
)
GEOCODE_URL = "https://geocodeservice.costco.com/Locations"

DEFAULT_PAGE_SIZE = 200
DEFAULT_DELAY = 1.0
MAX_RETRIES = 3


class CostcoAPIError(Exception):
    """Raised when the Costco API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(CostcoAPIError):
    """Raised when the API rate-limits us."""

    pass


class HttpTransport:
    """Low-level HTTP client for Costco Business Delivery APIs."""

    def __init__(
        self,
        api_key: str | None = None,
        delay: float = DEFAULT_DELAY,
        page_size: int = DEFAULT_PAGE_SIZE,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.environ.get("COSTCO_API_KEY") or DEFAULT_API_KEY
        self.delay = delay
        self.page_size = page_size
        self._last_request_time: float = 0

        self._client = httpx.Client(
            headers={
                "x-api-key": self.api_key,
                "origin": "https://www.costcobusinessdelivery.com",
                "referer": "https://www.costcobusinessdelivery.com/",
                "user-agent": f"costco-business-sdk/{_VERSION}",
                "accept": "*/*",
            },
            timeout=timeout,
        )

    def _throttle(self) -> None:
        """Enforce rate limiting between requests."""
        if self.delay <= 0:
            return
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request_time = time.monotonic()

    def _request(self, url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        """Make a GET request with rate limiting and retry logic."""
        self._throttle()

        for attempt in range(MAX_RETRIES):
            try:
                r = self._client.get(url, params=params)
            except httpx.TimeoutException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise CostcoAPIError(f"Request timed out after {MAX_RETRIES} attempts: {e}") from e

            if r.status_code == 429:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise RateLimitError(
                    f"Rate limited by API (429)", status_code=429
                )

            if r.status_code >= 500:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise CostcoAPIError(
                    f"Server error: {r.status_code}", status_code=r.status_code
                )

            if r.status_code != 200:
                raise CostcoAPIError(
                    f"API returned {r.status_code}: {r.text[:200]}", status_code=r.status_code
                )

            return r.json()

        raise CostcoAPIError("Max retries exceeded")

    def search(
        self,
        query: str = "*",
        location: str = "888",
        start: int = 0,
        rows: int | None = None,
    ) -> dict[str, Any]:
        """Execute a single search request."""
        return self._request(
            SEARCH_URL,
            params={
                "q": query,
                "start": str(start),
                "rows": str(rows or self.page_size),
                "locale": "en-US",
                "loc": location,
            },
        )

    def search_all(
        self,
        query: str = "*",
        location: str = "888",
    ) -> Iterator[dict]:
        """Iterate over all product documents, handling pagination."""
        # Get total count first
        data = self.search(query=query, location=location, start=0, rows=0)
        total = data.get("response", {}).get("numFound", 0)
        if total == 0:
            return

        pages = (total + self.page_size - 1) // self.page_size
        seen: set[str] = set()

        for page in range(pages):
            start = page * self.page_size
            data = self.search(query=query, location=location, start=start)
            docs = data.get("response", {}).get("docs", [])

            for doc in docs:
                item_id = doc.get("item_number", doc.get("id", ""))
                if item_id in seen:
                    continue
                seen.add(item_id)
                yield doc

            if len(docs) < self.page_size:
                break

    def count(self, query: str = "*", location: str = "888") -> int:
        """Get the total number of products matching a query."""
        data = self.search(query=query, location=location, start=0, rows=0)
        return data.get("response", {}).get("numFound", 0)

    def megamenu(self, location: str = "888") -> dict[str, Any]:
        """Fetch the category hierarchy."""
        return self._request(
            MEGAMENU_URL,
            params={"locale": "en-US", "loc": location, "chdmegamenu": "true"},
        )

    def geocode(self, zip_code: str) -> list[dict]:
        """Convert a zip code to geographic coordinates."""
        data = self._request(GEOCODE_URL, params={"q": zip_code})
        if isinstance(data, list):
            return data
        return [data] if data else []

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> HttpTransport:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
