"""Batch forecasting helpers for product-level demand planning."""

from __future__ import annotations

from demandiq.forecasting.model import DemandForecaster


def forecast_skus(
    histories: dict[str, list[float]], horizon: int = 7
) -> dict[str, list[float]]:
    """Forecast multiple SKUs independently and preserve their identifiers."""
    if not histories:
        raise ValueError("At least one SKU history is required.")
    results: dict[str, list[float]] = {}
    for sku, history in histories.items():
        normalized_sku = str(sku).strip()
        if not normalized_sku:
            raise ValueError("SKU identifiers must be non-empty.")
        if normalized_sku in results:
            raise ValueError(f"Duplicate normalized SKU identifier: {normalized_sku}")
        results[normalized_sku] = DemandForecaster().fit(history).predict(horizon)
    return results
