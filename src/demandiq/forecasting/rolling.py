"""Rolling-origin evaluation for more stable forecast comparisons."""

from __future__ import annotations

from demandiq.forecasting.metrics import mae, rmse, smape
from demandiq.forecasting.model import DemandForecaster


def rolling_backtest(
    history: list[float],
    *,
    horizon: int = 7,
    min_train_size: int = 21,
    step: int = 7,
) -> dict[str, object]:
    """Evaluate multiple expanding-window holdouts without random shuffling."""
    if horizon < 1 or min_train_size < 8 or step < 1:
        raise ValueError("Horizon, step, and minimum training size must be positive.")
    if len(history) < min_train_size + horizon:
        raise ValueError("History is too short for the requested rolling backtest.")

    windows: list[dict[str, object]] = []
    for cutoff in range(min_train_size, len(history) - horizon + 1, step):
        train = history[:cutoff]
        actual = history[cutoff:cutoff + horizon]
        predicted = DemandForecaster().fit(train).predict(horizon)
        windows.append({
            "train_size": cutoff,
            "actual": actual,
            "predicted": predicted,
            "mae": mae(actual, predicted),
            "rmse": rmse(actual, predicted),
            "smape": smape(actual, predicted),
        })
    if not windows:
        raise ValueError("No complete rolling holdout windows could be formed.")
    return {
        "windows": windows,
        "window_count": len(windows),
        "mean_mae": sum(float(item["mae"]) for item in windows) / len(windows),
        "mean_rmse": sum(float(item["rmse"]) for item in windows) / len(windows),
        "mean_smape": sum(float(item["smape"]) for item in windows) / len(windows),
    }
