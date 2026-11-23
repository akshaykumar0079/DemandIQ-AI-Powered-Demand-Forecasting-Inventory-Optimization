import pandas as pd
import pytest

from demandiq.data.csv_io import load_sales_csv, save_daily_sales


def test_csv_round_trip(tmp_path):
    source = tmp_path / "sales.csv"
    destination = tmp_path / "normalized" / "daily.csv"
    pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01"],
        "sku": ["A", "A"],
        "quantity": [2, 3],
    }).to_csv(source, index=False)
    frame = load_sales_csv(source)
    saved = save_daily_sales(frame, destination)
    assert saved.exists()
    assert load_sales_csv(saved)["quantity"].tolist() == [5]


def test_missing_csv_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_sales_csv(tmp_path / "missing.csv")
