import pytest

from demandiq.forecasting.baseline import seasonal_naive
from demandiq.forecasting.metrics import mae, rmse, smape


def test_seasonal_naive_repeats_latest_week():
    assert seasonal_naive([1, 2, 3, 4, 5, 6, 7], 9) == [1, 2, 3, 4, 5, 6, 7, 1, 2]


def test_seasonal_naive_uses_short_history_and_clips_negative_values():
    assert seasonal_naive([-1, 3], 3, 7) == [0.0, 3.0, 0.0]


@pytest.mark.parametrize("history,horizon", [([], 3), ([1], 0), ([float("nan")], 2)])
def test_invalid_forecast_input_is_rejected(history, horizon):
    with pytest.raises(ValueError):
        seasonal_naive(history, horizon)


def test_error_metrics_match_expected_values():
    assert mae([2, 4], [1, 6]) == 1.5
    assert rmse([2, 4], [1, 6]) == pytest.approx(2.5**0.5)
    assert smape([0, 0], [0, 0]) == 0.0


def test_metrics_reject_mismatched_lengths():
    with pytest.raises(ValueError):
        mae([1, 2], [1])
