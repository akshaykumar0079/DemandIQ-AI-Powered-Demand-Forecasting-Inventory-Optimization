# DemandIQ architecture

## Data flow

1. CSV ingestion reads product sales observations.
2. Validation checks the required `date`, `sku`, and non-negative whole-unit `quantity` fields.
3. Daily aggregation combines duplicate SKU/date rows. Missing dates are deliberately not filled because absence of a record is not necessarily zero demand.
4. Forecasting builds a seasonal-naive benchmark and a Random Forest regressor using lag-1, lag-7, rolling-seven-day mean, weekday index, and a time trend.
5. Evaluation uses chronological holdouts and reports MAE, RMSE, and sMAPE. Rolling-origin evaluation is available for expanding-window assessment.
6. Inventory policy converts forecast mean and variability, lead time, service factor, and stock position into safety stock, reorder point, and suggested order quantity.
7. FastAPI exposes these services. The React dashboard calls the API and displays forecast, inventory, and model comparison outputs.

## Model design

The Random Forest model is intentionally interpretable at the feature level and acts as a practical tabular baseline. Multi-step forecasts are recursive: each predicted day is appended to history before generating the next day. This can compound error over longer horizons, so compare results with the seasonal-naive benchmark and prefer short planning horizons until validated on representative data.

## Evaluation discipline

- Do not randomly shuffle time-series observations.
- Keep holdout periods strictly later than training periods.
- Compare candidate models on identical holdout dates.
- Report metrics alongside forecast horizon and data coverage.
- Evaluate by SKU; a strong aggregate score can hide poor performance for individual products.

## Inventory assumptions

The current policy is a heuristic. It uses population standard deviation of the supplied forecast and a configurable service factor to estimate safety stock. A full production policy would model lead-time demand distributions, service-level targets, open purchase orders, allocations, supplier constraints, minimum order quantities, and review cycles.
