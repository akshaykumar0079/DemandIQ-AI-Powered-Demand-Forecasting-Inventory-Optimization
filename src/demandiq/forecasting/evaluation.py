"""Chronological comparison utilities for forecasting candidates."""

from __future__ import annotations

from demandiq.forecasting.baseline import seasonal_naive
from demandiq.forecasting.metrics import mae, rmse, smape
from demandiq.forecasting.model import DemandForecaster


def compare_forecasters(history: list[float], horizon: int = 7) -> dict[str, object]:
    """Compare candidate models on the same chronological holdout window."""
    if horizon < 1 or horizon > 30:
        raise ValueError("Comparison horizon must be between 1 and 30 days.")
    if len(history) < horizon + 22:
        raise ValueError("History must include at least 22 training and horizon test days.")

    train = history[:-horizon]
    actual = history[-horizon:]
    candidates = {
        "seasonal_naive": seasonal_naive(train, horizon),
        "random_forest": DemandForecaster().fit(train).predict(horizon),
    }
    results: dict[str, dict[str, float]] = {}
    for name, predicted in candidates.items():
        results[name] = {
            "mae": mae(actual, predicted),
            "rmse": rmse(actual, predicted),
            "smape": smape(actual, predicted),
        }
    winner = min(results, key=lambda name: results[name]["mae"])
    return {"actual": actual, "models": results, "recommended_model": winner}
