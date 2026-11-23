"""Forecast evaluation metrics for non-negative demand series."""

from __future__ import annotations

import numpy as np


def mae(actual: list[float] | np.ndarray, predicted: list[float] | np.ndarray) -> float:
    """Mean absolute error."""
    y_true, y_pred = _aligned_arrays(actual, predicted)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(actual: list[float] | np.ndarray, predicted: list[float] | np.ndarray) -> float:
    """Root mean squared error."""
    y_true, y_pred = _aligned_arrays(actual, predicted)
    return float(np.sqrt(np.mean(np.square(y_true - y_pred))))


def smape(actual: list[float] | np.ndarray, predicted: list[float] | np.ndarray) -> float:
    """Symmetric mean absolute percentage error, expressed from 0 to 200."""
    y_true, y_pred = _aligned_arrays(actual, predicted)
    denominator = np.abs(y_true) + np.abs(y_pred)
    terms = np.divide(
        2.0 * np.abs(y_pred - y_true),
        denominator,
        out=np.zeros_like(denominator, dtype=float),
        where=denominator != 0,
    )
    return float(100.0 * np.mean(terms))


def _aligned_arrays(
    actual: list[float] | np.ndarray, predicted: list[float] | np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    y_true = np.asarray(actual, dtype=float)
    y_pred = np.asarray(predicted, dtype=float)
    if y_true.ndim != 1 or y_pred.ndim != 1:
        raise ValueError("Actual and predicted values must be one-dimensional.")
    if y_true.size == 0 or y_true.size != y_pred.size:
        raise ValueError("Actual and predicted values must have equal, non-zero lengths.")
    if not np.isfinite(y_true).all() or not np.isfinite(y_pred).all():
        raise ValueError("Actual and predicted values must be finite.")
    return y_true, y_pred
