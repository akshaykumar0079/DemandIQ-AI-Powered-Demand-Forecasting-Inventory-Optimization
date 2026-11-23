import pytest

from demandiq.inventory.risk import classify_inventory_risk


@pytest.mark.parametrize(
    "on_hand,expected",
    [(5, "stockout_risk"), (11, "healthy"), (30, "overstock_risk")],
)
def test_inventory_risk_classification(on_hand, expected):
    result = classify_inventory_risk(on_hand=on_hand, reorder_point=10, target_stock=20)
    assert result["status"] == expected


def test_inventory_risk_rejects_inconsistent_thresholds():
    with pytest.raises(ValueError):
        classify_inventory_risk(on_hand=10, reorder_point=20, target_stock=15)
