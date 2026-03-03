"""Shared test fixtures."""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def search_response():
    """A real search API response with a few products."""
    return json.loads((FIXTURES / "search_response.json").read_text())


@pytest.fixture
def megamenu_response():
    """A real megamenu API response."""
    return json.loads((FIXTURES / "megamenu_response.json").read_text())
