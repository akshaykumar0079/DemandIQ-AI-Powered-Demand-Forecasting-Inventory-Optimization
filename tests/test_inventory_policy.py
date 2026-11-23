import pytest

from demandiq.inventory.policy import recommend_replenishment


def test_recommendation_calculates_target_and_order_quantity():
    result = recommend_replenishment([10,10,10,10], on_hand=15, lead_time_days=2,
                                    service_factor=1.0, review_period_days=3)
    assert result.average_daily_demand == 10
    assert result.safety_stock == 0
    assert result.reorder_point == 20
    assert result.suggested_order_quantity == 35


def test_variable_demand_adds_safety_stock():
    result = recommend_replenishment([0,10,20], on_hand=0, lead_time_days=4)
    assert result.safety_stock > 0
    assert result.suggested_order_quantity >= result.reorder_point


@pytest.mark.parametrize("kwargs", [
    {"on_hand":-1,"lead_time_days":2},
    {"on_hand":1,"lead_time_days":-2},
    {"on_hand":1,"lead_time_days":2,"service_factor":-1},
])
def test_invalid_inventory_parameters_are_rejected(kwargs):
    with pytest.raises(ValueError):
        recommend_replenishment([5,6], **kwargs)


def test_empty_forecast_is_rejected():
    with pytest.raises(ValueError):
        recommend_replenishment([], on_hand=0, lead_time_days=2)

def test_inventory_position_includes_inbound_and_allocated_units():
    result = recommend_replenishment(
        [10, 10, 10], on_hand=20, on_order=15, allocated=5,
        lead_time_days=2, review_period_days=1, service_factor=0,
    )
    assert result.inventory_position == 30
    assert result.target_stock == 30
    assert result.suggested_order_quantity == 0
