"""Simple forecasting baselines used as transparent benchmarks."""

from __future__ import annotations

import numpy as np


def seasonal_naive(
    history: list[float] | np.ndarray, horizon: int, season_length: int = 7
) -> list[float]:
    """Repeat the latest complete seasonal pattern into the forecast horizon.

    If fewer than one full season is available, repeat the available history.
    Values are clipped at zero because demand cannot be negative.
    """
    values = np.asarray(history, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("History must contain at least one observation.")
    if not np.isfinite(values).all():
        raise ValueError("History values must be finite.")
    if horizon < 1:
        raise ValueError("Horizon must be at least one day.")
    if season_length < 1:
        raise ValueError("Season length must be at least one.")
    pattern = np.maximum(values[-min(season_length, values.size):], 0.0)
    return np.resize(pattern, horizon).astype(float).tolist()
