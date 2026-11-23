"""Run a small end-to-end DemandIQ forecast from a sales CSV."""

from __future__ import annotations

import argparse
import json

from demandiq.data.csv_io import load_sales_csv
from demandiq.forecasting.model import DemandForecaster


def main() -> None:
    parser = argparse.ArgumentParser(description="Forecast SKU demand from a daily sales CSV.")
    parser.add_argument(
        "csv_path", help="Path to a CSV containing date, sku, and quantity columns."
    )
    parser.add_argument("--horizon", type=int, default=7, help="Number of days to forecast.")
    args = parser.parse_args()

    frame = load_sales_csv(args.csv_path)
    output: dict[str, list[float]] = {}
    for sku, group in frame.groupby("sku", sort=True):
        history = group.sort_values("date")["quantity"].astype(float).tolist()
        if len(history) < 8:
            continue
        output[str(sku)] = DemandForecaster().fit(history).predict(args.horizon)
    print(json.dumps({"horizon": args.horizon, "forecasts": output}, indent=2))


if __name__ == "__main__":
    main()
