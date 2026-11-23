"""Simple inventory exposure classification based on planning thresholds."""

from __future__ import annotations


def classify_inventory_risk(
    *,
    on_hand: int,
    reorder_point: int,
    target_stock: int,
) -> dict[str, str | int]:
    """Classify current stock relative to reorder and target stock levels."""
    if min(on_hand, reorder_point, target_stock) < 0:
        raise ValueError("Inventory levels must be non-negative.")
    if target_stock < reorder_point:
        raise ValueError("Target stock must be greater than or equal to reorder point.")

    if on_hand <= reorder_point:
        status = "stockout_risk"
        message = "Stock is at or below the reorder point."
    elif on_hand > target_stock:
        status = "overstock_risk"
        message = "Stock is above the target inventory level."
    else:
        status = "healthy"
        message = "Stock is within the planned operating range."
    return {
        "status": status,
        "message": message,
        "on_hand": on_hand,
        "reorder_point": reorder_point,
        "target_stock": target_stock,
    }
