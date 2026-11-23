import pytest

from demandiq.forecasting.evaluation import compare_forecasters


def test_comparison_returns_metrics_for_both_candidates():
    history = [float(10 + index % 7) for index in range(42)]
    result = compare_forecasters(history, horizon=7)
    assert set(result["models"]) == {"seasonal_naive", "random_forest"}
    assert result["recommended_model"] in result["models"]
    assert set(result["models"]["random_forest"]) == {"mae", "rmse", "smape"}


def test_comparison_rejects_insufficient_history():
    with pytest.raises(ValueError):
        compare_forecasters([1.0] * 20, horizon=7)
