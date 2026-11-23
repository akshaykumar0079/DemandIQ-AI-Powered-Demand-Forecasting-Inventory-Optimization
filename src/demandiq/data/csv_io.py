"""CSV boundary helpers for sales history."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from demandiq.data.validation import aggregate_daily_sales


def load_sales_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV file and return validated daily SKU aggregates."""
    source = Path(path)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Sales CSV not found: {source}")
    try:
        frame = pd.read_csv(source)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not read sales CSV: {exc}") from exc
    return aggregate_daily_sales(frame)


def save_daily_sales(frame: pd.DataFrame, path: str | Path) -> Path:
    """Validate and write daily sales aggregates to a CSV file."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    clean = aggregate_daily_sales(frame)
    clean.to_csv(destination, index=False, date_format="%Y-%m-%d")
    return destination
