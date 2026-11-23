"""Transparent inventory replenishment policy calculations."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ReplenishmentRecommendation:
    """Calculated replenishment quantities for a single SKU."""

    average_daily_demand: float
    safety_stock: int
    reorder_point: int
    inventory_position: int
    suggested_order_quantity: int


def recommend_replenishment(
    forecast: list[float],
    *,
    on_hand: int,
    lead_time_days: int,
    service_factor: float = 1.65,
    review_period_days: int = 0,
) -> ReplenishmentRecommendation:
    """Calculate a simple demand-variability-based reorder recommendation.

    The forecast should contain daily unit demand over a representative period.
    Safety stock uses population standard deviation times service factor and
    square-root lead-time scaling. This is a planning heuristic, not a guarantee.
    """
    if not forecast:
        raise ValueError("Forecast must contain at least one daily value.")
    if any(not math.isfinite(float(value)) or float(value) < 0 for value in forecast):
        raise ValueError("Forecast values must be finite and non-negative.")
    if on_hand < 0 or lead_time_days < 0 or review_period_days < 0:
        raise ValueError("Stock and day counts must be non-negative.")
    if service_factor < 0 or not math.isfinite(service_factor):
        raise ValueError("Service factor must be finite and non-negative.")

    mean_demand = sum(float(value) for value in forecast) / len(forecast)
    variance = sum((float(value) - mean_demand) ** 2 for value in forecast) / len(forecast)
    safety = math.ceil(service_factor * math.sqrt(variance) * math.sqrt(lead_time_days))
    reorder_point = math.ceil(mean_demand * lead_time_days) + safety
    target_stock = math.ceil(mean_demand * (lead_time_days + review_period_days)) + safety
    inventory_position = on_hand
    suggested = max(0, target_stock - inventory_position)
    return ReplenishmentRecommendation(
        average_daily_demand=mean_demand,
        safety_stock=safety,
        reorder_point=reorder_point,
        inventory_position=inventory_position,
        suggested_order_quantity=suggested,
    )
