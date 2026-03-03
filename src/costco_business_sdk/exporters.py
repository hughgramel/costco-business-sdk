"""Export products to CSV, JSON, and Rich tables."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from rich.table import Table

from .models import CSV_FIELDS, Product


def to_csv(products: list[Product], path: Path) -> Path:
    """Write products to a CSV file.

    Includes a ``fetched_at`` column with the export timestamp.
    """
    fetched_at = datetime.now(timezone.utc).isoformat()
    fields = [*CSV_FIELDS, "fetched_at"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in products:
            row = p.to_dict()
            row["fetched_at"] = fetched_at
            writer.writerow(row)

    return path


def to_json(products: list[Product], path: Path, indent: int = 2) -> Path:
    """Write products to a JSON file.

    Includes a ``fetched_at`` field with the export timestamp.
    """
    fetched_at = datetime.now(timezone.utc).isoformat()
    data = {
        "fetched_at": fetched_at,
        "count": len(products),
        "products": [p.to_dict() for p in products],
    }
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False))
    return path


def to_table(
    products: list[Product],
    columns: list[str] | None = None,
    title: str | None = None,
    max_rows: int = 50,
) -> Table:
    """Create a Rich table for terminal display.

    Args:
        products: Products to display.
        columns: Which fields to show. Defaults to a useful subset.
        title: Optional table title.
        max_rows: Maximum rows to show.
    """
    if columns is None:
        columns = ["item_number", "name", "brand", "list_price", "sale_price", "discount_pct", "stock_status"]

    table = Table(title=title, show_lines=False)
    for col in columns:
        justify = "right" if col in ("list_price", "sale_price", "discount_pct", "rating", "review_count") else "left"
        table.add_column(col, justify=justify)

    for p in products[:max_rows]:
        d = p.to_dict()
        row = []
        for col in columns:
            val = d.get(col, "")
            if col in ("list_price", "sale_price") and isinstance(val, (int, float)) and val > 0:
                row.append(f"${val:.2f}")
            elif col == "discount_pct" and isinstance(val, (int, float)) and val > 0:
                row.append(f"{val}%")
            elif col == "name" and isinstance(val, str) and len(val) > 60:
                row.append(val[:57] + "...")
            else:
                row.append(str(val))
        table.add_row(*row)

    if len(products) > max_rows:
        table.caption = f"Showing {max_rows} of {len(products)} results"

    return table
