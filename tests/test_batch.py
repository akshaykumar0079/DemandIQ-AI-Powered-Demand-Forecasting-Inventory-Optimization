import pytest

from demandiq.forecasting.batch import forecast_skus


def test_batch_forecasts_each_sku_independently():
    histories = {
        "SKU-A": [float(5 + index % 4) for index in range(28)],
        "SKU-B": [float(12 + index % 3) for index in range(28)],
    }
    result = forecast_skus(histories, horizon=4)
    assert set(result) == {"SKU-A", "SKU-B"}
    assert len(result["SKU-A"]) == 4
    assert len(result["SKU-B"]) == 4


def test_batch_rejects_empty_and_blank_sku_inputs():
    with pytest.raises(ValueError):
        forecast_skus({})
    with pytest.raises(ValueError):
        forecast_skus({" ": [1.0] * 10})
