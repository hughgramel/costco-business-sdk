"""Tests for location registry and discovery."""

from costco_business_sdk.locations import (
    BUSINESS_CENTERS,
    find_nearest_by_coords,
    get_all_locations,
)


def test_business_centers_registry():
    """Registry contains known Business Centers."""
    assert "115" in BUSINESS_CENTERS
    assert BUSINESS_CENTERS["115"]["city"] == "LYNNWOOD"
    assert BUSINESS_CENTERS["115"]["state"] == "WA"


def test_get_all_locations():
    """get_all_locations returns Location objects."""
    locs = get_all_locations()
    assert len(locs) == len(BUSINESS_CENTERS)
    assert all(loc.id in BUSINESS_CENTERS for loc in locs)


def test_find_nearest_by_coords():
    """find_nearest_by_coords returns locations sorted by distance."""
    # Coordinates near Lynnwood, WA
    locs = find_nearest_by_coords(47.82, -122.31, limit=3)

    assert len(locs) <= 3
    assert locs[0].id == "115"  # Lynnwood should be closest
    assert locs[0].distance_mi is not None
    assert locs[0].distance_mi < 5  # Should be very close

    # Distances should be sorted
    distances = [l.distance_mi for l in locs]
    assert distances == sorted(distances)


def test_find_nearest_east_coast():
    """Find nearest from East Coast should return Hackensack."""
    # Coordinates near New York City
    locs = find_nearest_by_coords(40.7128, -74.0060, limit=3)

    # One of the Hackensack locations should be first
    assert locs[0].state == "NJ"
