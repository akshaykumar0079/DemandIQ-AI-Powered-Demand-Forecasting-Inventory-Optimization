import pandas as pd
import pytest

from demandiq.data.validation import SalesDataError, aggregate_daily_sales, validate_sales_frame


def test_validation_normalizes_dates_skus_and_quantities():
    frame = pd.DataFrame({"date":["2026-01-02","2026-01-01"],"sku":[" A ","A"],"quantity":["2","3"]})
    result = validate_sales_frame(frame)
    assert result["sku"].tolist() == ["A", "A"]
    assert result["quantity"].tolist() == [3, 2]
    assert str(result["date"].dtype).startswith("datetime64")


def test_aggregation_combines_duplicate_sku_day_rows():
    frame = pd.DataFrame({"date":["2026-01-01","2026-01-01"],"sku":["A","A"],"quantity":[2,4]})
    result = aggregate_daily_sales(frame)
    assert result.to_dict("records") == [{"date":pd.Timestamp("2026-01-01"),"sku":"A","quantity":6}]


@pytest.mark.parametrize("frame", [
    pd.DataFrame({"date":["2026-01-01"],"sku":["A"]}),
    pd.DataFrame({"date":["bad"],"sku":["A"],"quantity":[1]}),
    pd.DataFrame({"date":["2026-01-01"],"sku":["A"],"quantity":[-1]}),
    pd.DataFrame({"date":["2026-01-01"],"sku":[" "],"quantity":[1]}),
    pd.DataFrame({"date":["2026-01-01"],"sku":["A"],"quantity":[1.5]}),
])
def test_invalid_sales_input_is_rejected(frame):
    with pytest.raises(SalesDataError):
        validate_sales_frame(frame)


def test_empty_frame_is_rejected():
    with pytest.raises(SalesDataError, match="no rows"):
        validate_sales_frame(pd.DataFrame(columns=["date","sku","quantity"]))
