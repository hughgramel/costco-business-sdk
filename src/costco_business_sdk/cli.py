"""CLI interface for the Costco Business SDK."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.tree import Tree

from .client import CostcoBusiness
from .exporters import to_csv, to_json, to_table

app = typer.Typer(
    name="costco-biz",
    help="Python SDK for the Costco Business Delivery product search API.",
    no_args_is_help=True,
)
console = Console()


def _get_client(location: str | None = None, delay: float = 1.0) -> CostcoBusiness:
    return CostcoBusiness(location=location, delay=delay)


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query (e.g., 'coffee')")],
    location: Annotated[Optional[str], typer.Option("--location", "-l", help="Warehouse ID")] = None,
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 20,
    format: Annotated[str, typer.Option("--format", "-f", help="Output format: table, csv, json")] = "table",
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path")] = None,
) -> None:
    """Search for products by keyword."""
    client = _get_client(location)
    loc = location or "888"
    console.print(f"Searching for [bold]{query}[/] at location {loc}...")

    products = client.search(query, location=location, limit=limit)
    console.print(f"Found {len(products)} products.\n")

    _output_results(products, format, output)
    client.close()


@app.command()
def deals(
    location: Annotated[Optional[str], typer.Option("--location", "-l", help="Warehouse ID")] = None,
    min_discount: Annotated[float, typer.Option("--min-discount", help="Minimum discount %")] = 0,
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 50,
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "table",
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path")] = None,
) -> None:
    """Find products currently on sale."""
    client = _get_client(location)
    loc = location or "888"
    console.print(f"Finding deals at location {loc} (min {min_discount}% off)...")

    all_deals = client.deals(location=location, min_discount=min_discount)
    console.print(f"Found {len(all_deals)} deals.\n")

    _output_results(all_deals[:limit], format, output)
    client.close()


@app.command()
def categories(
    location: Annotated[Optional[str], typer.Option("--location", "-l", help="Warehouse ID")] = None,
) -> None:
    """Browse the product category tree."""
    client = _get_client(location)
    cats = client.categories(location=location)

    tree = Tree("[bold]Categories[/]")
    for cat in cats:
        _add_category_to_tree(tree, cat)

    console.print(tree)
    client.close()


def _add_category_to_tree(parent: Tree, cat) -> None:
    label = f"{cat.name} ({cat.count})" if cat.count else cat.name
    node = parent.add(label)
    for child in cat.children:
        _add_category_to_tree(node, child)


@app.command()
def dump(
    location: Annotated[str, typer.Option("--location", "-l", help="Warehouse ID")] = "888",
    format: Annotated[str, typer.Option("--format", "-f", help="csv or json")] = "csv",
    output: Annotated[Path, typer.Option("--output", "-o", help="Output directory")] = Path("."),
) -> None:
    """Export the full product catalog for a location."""
    client = _get_client(location)
    console.print(f"Dumping full catalog for location {location}...")

    products = client.dump(location=location)
    console.print(f"Fetched {len(products)} products.")

    output.mkdir(parents=True, exist_ok=True)

    if format == "csv":
        path = to_csv(products, output / f"products_{location}.csv")
        console.print(f"Saved: {path} ({path.stat().st_size / 1_048_576:.1f} MB)")
    elif format == "json":
        path = to_json(products, output / f"products_{location}.json")
        console.print(f"Saved: {path} ({path.stat().st_size / 1_048_576:.1f} MB)")

    client.close()


@app.command()
def nearest(
    zip_code: Annotated[str, typer.Argument(help="US zip code (e.g., 98105)")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 5,
) -> None:
    """Find the nearest Business Centers to a zip code."""
    client = _get_client()
    locs = client.find_nearest(zip_code, limit=limit)

    from rich.table import Table

    table = Table(title=f"Nearest Business Centers to {zip_code}")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("City")
    table.add_column("State")
    table.add_column("Distance", justify="right")

    for loc in locs:
        dist = f"{loc.distance_mi:.1f} mi" if loc.distance_mi is not None else "?"
        table.add_row(loc.id, loc.name, loc.city, loc.state, dist)

    console.print(table)
    console.print(
        "\n[dim]Tip: You can also see your active location in the footer of costcobusinessdelivery.com[/]"
    )
    client.close()


@app.command(name="locations")
def list_locations() -> None:
    """List all known Costco Business Center locations."""
    client = _get_client()
    locs = client.locations()

    from rich.table import Table

    table = Table(title=f"Costco Business Centers ({len(locs)} locations)")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("City")
    table.add_column("State")
    table.add_column("Zip")

    for loc in sorted(locs, key=lambda l: (l.state, l.city)):
        table.add_row(loc.id, loc.name, loc.city, loc.state, loc.zip_code)

    console.print(table)
    client.close()


@app.command()
def count(
    query: Annotated[str, typer.Argument(help="Search query")] = "*",
    location: Annotated[Optional[str], typer.Option("--location", "-l", help="Warehouse ID")] = None,
) -> None:
    """Count products matching a query."""
    client = _get_client(location)
    loc = location or "888"
    n = client.count(query=query, location=location)
    console.print(f"Location {loc}: [bold]{n:,}[/] products matching '{query}'")
    client.close()


def _output_results(products: list, format: str, output: Path | None) -> None:
    """Output products in the requested format."""
    if format == "table":
        console.print(to_table(products))
    elif format == "csv" and output:
        to_csv(products, output)
        console.print(f"Saved to {output}")
    elif format == "json" and output:
        to_json(products, output)
        console.print(f"Saved to {output}")
    elif format in ("csv", "json") and not output:
        console.print(f"[red]--output is required for {format} format[/]")
    else:
        console.print(to_table(products))
