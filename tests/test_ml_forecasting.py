import numpy as np
import pytest

from demandiq.forecasting.features import build_training_frame
from demandiq.forecasting.model import DemandForecaster, chronological_backtest


def test_feature_builder_creates_expected_lag_columns():
    features, target = build_training_frame(list(range(1, 11)))
    assert list(features.columns) == ["lag_1", "lag_7", "rolling_mean_7", "day_of_week", "trend"]
    assert len(features) == 3
    assert target.tolist() == [8.0, 9.0, 10.0]
    assert features.iloc[0]["lag_7"] == 1.0


def test_random_forest_forecasts_non_negative_values():
    history = [10 + (index % 7) for index in range(42)]
    predictions = DemandForecaster(n_estimators=30).fit(history).predict(5)
    assert len(predictions) == 5
    assert all(value >= 0 for value in predictions)


def test_model_requires_fit_and_valid_horizon():
    model = DemandForecaster()
    with pytest.raises(RuntimeError):
        model.predict(3)
    with pytest.raises(ValueError):
        model.fit([1, 2, 3, 4, 5, 6, 7])


def test_chronological_backtest_keeps_holdout_order():
    history = [float(5 + index % 5) for index in range(35)]
    result = chronological_backtest(history, horizon=5)
    assert result["actual"] == history[-5:]
    assert len(result["predicted"]) == 5


def test_backtest_rejects_short_history():
    with pytest.raises(ValueError):
        chronological_backtest(list(np.ones(20)), horizon=5)
