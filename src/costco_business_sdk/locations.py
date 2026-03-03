"""Costco Business Center location registry and discovery."""

from __future__ import annotations

import math
from functools import lru_cache

from .models import Location

# All known Costco Business Center locations.
# Discovered by scanning the search API (IDs 1-1000) and cross-referencing
# with costcobusinessdelivery.com warehouse pages.
#
# IDs below 1000 were found by probing the search API. IDs above 1000 are
# newer locations found via web search (the scan only covered 1-1000).
#
# fmt: off
BUSINESS_CENTERS: dict[str, dict] = {
    # ── Found via search API scan (IDs 1-1000, have pricing) ──
    "10":   {"name": "Hackensack Bus Ctr",      "city": "HACKENSACK",         "state": "NJ", "zip": "07601",      "lat": 40.8870,  "lon": -74.0465},
    "25":   {"name": "Unknown Bus Ctr",          "city": "UNKNOWN",            "state": "??", "zip": "",           "lat": 0.0,      "lon": 0.0},
    "63":   {"name": "NE Anchorage",             "city": "ANCHORAGE",          "state": "AK", "zip": "99515",      "lat": 61.1441,  "lon": -149.8675},
    "113":  {"name": "Salt Lake City Bus Ctr",   "city": "SALT LAKE CITY",     "state": "UT", "zip": "84104",      "lat": 40.7608,  "lon": -111.8910},
    "115":  {"name": "Lynnwood Bus Ctr",         "city": "LYNNWOOD",           "state": "WA", "zip": "98036-5228", "lat": 47.8257,  "lon": -122.3105},
    "563":  {"name": "Las Vegas Bus Ctr",        "city": "LAS VEGAS",          "state": "NV", "zip": "89118",      "lat": 36.0932,  "lon": -115.2006},
    "564":  {"name": "Hawthorne Bus Ctr",        "city": "HAWTHORNE",          "state": "CA", "zip": "90250",      "lat": 33.9164,  "lon": -118.3526},
    "569":  {"name": "Commerce Bus Ctr",         "city": "COMMERCE",           "state": "CA", "zip": "90040",      "lat": 34.0005,  "lon": -118.1568},
    "578":  {"name": "San Diego Bus Ctr",        "city": "SAN DIEGO",          "state": "CA", "zip": "92154",      "lat": 32.6409,  "lon": -117.0490},
    "579":  {"name": "Morrow Bus Ctr",           "city": "MORROW",             "state": "GA", "zip": "30260",      "lat": 33.5832,  "lon": -84.3360},
    "580":  {"name": "Bedford Park Bus Ctr",     "city": "CHICAGO",            "state": "IL", "zip": "60638",      "lat": 41.7700,  "lon": -87.8050},
    "650":  {"name": "Denver Bus Ctr",           "city": "DENVER",             "state": "CO", "zip": "80216",      "lat": 39.7817,  "lon": -104.9700},
    "651":  {"name": "Orlando Bus Ctr",          "city": "ORLANDO",            "state": "FL", "zip": "32809",      "lat": 28.4912,  "lon": -81.3962},
    "652":  {"name": "Minneapolis Bus Ctr",      "city": "MINNEAPOLIS",        "state": "MN", "zip": "55418",      "lat": 44.9986,  "lon": -93.2465},
    "653":  {"name": "Burbank Bus Ctr",          "city": "NORTH HOLLYWOOD",    "state": "CA", "zip": "91505",      "lat": 34.1808,  "lon": -118.3090},
    "654":  {"name": "S San Francisco Bus Ctr",  "city": "SOUTH SAN FRANCISCO","state": "CA", "zip": "94080",      "lat": 37.6547,  "lon": -122.4077},
    "655":  {"name": "Dallas Bus Ctr",           "city": "DALLAS",             "state": "TX", "zip": "75247",      "lat": 32.8104,  "lon": -96.8747},
    "729":  {"name": "Hackensack Bus Ctr",       "city": "HACKENSACK",         "state": "NJ", "zip": "07601",      "lat": 40.8870,  "lon": -74.0465},
    "767":  {"name": "Fife Bus Ctr",             "city": "FIFE",               "state": "WA", "zip": "98424",      "lat": 47.2329,  "lon": -122.3570},
    "823":  {"name": "Hayward Bus Ctr",          "city": "HAYWARD",            "state": "CA", "zip": "94545",      "lat": 37.6338,  "lon": -122.0967},
    "827":  {"name": "Phoenix Bus Ctr",          "city": "PHOENIX",            "state": "AZ", "zip": "85008",      "lat": 33.4576,  "lon": -111.9888},
    "848":  {"name": "San Jose Bus Ctr",         "city": "SAN JOSE",           "state": "CA", "zip": "95112",      "lat": 37.3675,  "lon": -121.9092},
    "893":  {"name": "Sacramento Bus Ctr",       "city": "SACRAMENTO",         "state": "CA", "zip": "95828",      "lat": 38.5025,  "lon": -121.4273},
    "943":  {"name": "Westminster Bus Ctr",      "city": "WESTMINSTER",        "state": "CA", "zip": "92683",      "lat": 33.7513,  "lon": -117.9940},
    "947":  {"name": "Ontario Bus Ctr",          "city": "ONTARIO",            "state": "CA", "zip": "91761",      "lat": 34.0633,  "lon": -117.6509},
    # ── Newer locations (IDs > 1000, found via web search) ──
    "1487": {"name": "Stafford Bus Ctr",         "city": "STAFFORD",           "state": "TX", "zip": "77477",      "lat": 29.6156,  "lon": -95.5569},
    "1581": {"name": "San Marcos Bus Ctr",       "city": "SAN MARCOS",         "state": "CA", "zip": "92078",      "lat": 33.1434,  "lon": -117.1661},
    "1661": {"name": "Anchorage Bus Ctr",        "city": "ANCHORAGE",          "state": "AK", "zip": "99515",      "lat": 61.1441,  "lon": -149.8675},
    "1663": {"name": "Southfield Bus Ctr",       "city": "SOUTHFIELD",         "state": "MI", "zip": "48075",      "lat": 42.4734,  "lon": -83.2219},
    "1665": {"name": "St. Louis Bus Ctr",        "city": "ST. LOUIS",          "state": "MO", "zip": "63114",      "lat": 38.6854,  "lon": -90.3486},
}
# fmt: on


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in miles between two lat/lon points."""
    R = 3958.8  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def get_all_locations() -> list[Location]:
    """Return Location objects for all known Business Centers."""
    return [
        Location(
            id=wid,
            name=info["name"],
            address="",
            city=info["city"],
            state=info["state"],
            zip_code=info["zip"],
            latitude=info["lat"],
            longitude=info["lon"],
        )
        for wid, info in BUSINESS_CENTERS.items()
    ]


def find_nearest_by_coords(
    latitude: float,
    longitude: float,
    limit: int = 5,
) -> list[Location]:
    """Find the nearest Business Centers to a given lat/lon."""
    locations = get_all_locations()
    for loc in locations:
        loc.distance_mi = round(_haversine(latitude, longitude, loc.latitude, loc.longitude), 1)
    locations.sort(key=lambda l: l.distance_mi or float("inf"))
    return locations[:limit]
