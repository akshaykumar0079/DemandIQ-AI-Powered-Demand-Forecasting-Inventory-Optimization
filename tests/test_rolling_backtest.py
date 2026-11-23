import pytest

from demandiq.forecasting.rolling import rolling_backtest


def test_rolling_backtest_returns_multiple_chronological_windows():
    history = [float(8 + index % 5) for index in range(50)]
    result = rolling_backtest(history, horizon=5, min_train_size=20, step=5)
    assert result["window_count"] == 6
    assert len(result["windows"]) == 6
    assert result["mean_mae"] >= 0
    assert result["mean_rmse"] >= 0


def test_rolling_backtest_rejects_short_history():
    with pytest.raises(ValueError):
        rolling_backtest([1.0] * 15, horizon=7, min_train_size=14)
