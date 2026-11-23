"""Feature construction for univariate daily demand forecasting."""

from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = ["lag_1", "lag_7", "rolling_mean_7", "day_of_week", "trend"]


def build_training_frame(values: list[float] | np.ndarray) -> tuple[pd.DataFrame, pd.Series]:
    """Build leakage-safe supervised rows from an ordered daily demand series."""
    series = np.asarray(values, dtype=float)
    if series.ndim != 1 or series.size < 8:
        raise ValueError("At least 8 daily observations are required to build lag features.")
    if not np.isfinite(series).all() or (series < 0).any():
        raise ValueError("Demand history must contain finite, non-negative values.")

    rows: list[dict[str, float]] = []
    targets: list[float] = []
    for index in range(7, series.size):
        rows.append({
            "lag_1": float(series[index - 1]),
            "lag_7": float(series[index - 7]),
            "rolling_mean_7": float(np.mean(series[index - 7:index])),
            "day_of_week": float(index % 7),
            "trend": float(index),
        })
        targets.append(float(series[index]))
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS), pd.Series(targets, name="demand")


def next_day_features(history: list[float], index: int) -> pd.DataFrame:
    """Create a single feature row for recursive one-step prediction."""
    if len(history) < 7:
        raise ValueError("At least 7 observations are required for prediction.")
    return pd.DataFrame([{
        "lag_1": float(history[-1]),
        "lag_7": float(history[-7]),
        "rolling_mean_7": float(np.mean(history[-7:])),
        "day_of_week": float(index % 7),
        "trend": float(index),
    }], columns=FEATURE_COLUMNS)
