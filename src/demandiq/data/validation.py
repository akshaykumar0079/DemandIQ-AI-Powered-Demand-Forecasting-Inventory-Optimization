"""Validation helpers for product-level sales history."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"date", "sku", "quantity"}


class SalesDataError(ValueError):
    """Raised when sales input violates the documented data contract."""


def validate_sales_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a normalized copy of sales data or raise a helpful error.

    The function deliberately does not fill absent calendar dates: a missing
    observation is not necessarily evidence of zero demand.
    """
    if not isinstance(frame, pd.DataFrame):
        raise SalesDataError("Sales input must be a pandas DataFrame.")
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise SalesDataError(f"Missing required columns: {', '.join(sorted(missing))}")
    if frame.empty:
        raise SalesDataError("Sales input contains no rows.")

    result = frame.copy()
    try:
        result["date"] = pd.to_datetime(result["date"], errors="raise").dt.normalize()
        result["quantity"] = pd.to_numeric(result["quantity"], errors="raise")
    except (TypeError, ValueError) as exc:
        raise SalesDataError(f"Invalid date or quantity value: {exc}") from exc

    if result["sku"].isna().any() or result["sku"].astype(str).str.strip().eq("").any():
        raise SalesDataError("SKU values must be present and non-empty.")
    if result["quantity"].isna().any():
        raise SalesDataError("Quantity values must not be missing.")
    if (result["quantity"] < 0).any():
        raise SalesDataError("Quantity values must be non-negative.")
    if not result["quantity"].map(lambda value: float(value).is_integer()).all():
        raise SalesDataError("Quantity values must be whole units.")

    result["sku"] = result["sku"].astype(str).str.strip()
    result["quantity"] = result["quantity"].astype(int)
    return result.sort_values(["sku", "date"], kind="stable").reset_index(drop=True)


def aggregate_daily_sales(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate duplicate SKU/date rows into one daily demand observation."""
    clean = validate_sales_frame(frame)
    return (
        clean.groupby(["date", "sku"], as_index=False, sort=True)["quantity"]
        .sum()
        .sort_values(["sku", "date"], kind="stable")
        .reset_index(drop=True)
    )
