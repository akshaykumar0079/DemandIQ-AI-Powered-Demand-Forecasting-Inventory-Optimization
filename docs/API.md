# DemandIQ API

Start the service locally:

```bash
uvicorn demandiq.api.main:app --reload
```

Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service health |
| POST | `/sales/observations` | Persist or update daily SKU sales observations |
| GET | `/sales/skus` | List SKUs with stored observations |
| GET | `/sales/{sku}/history` | Read a SKU's stored daily sales history |
| POST | `/forecast/baseline` | Seasonal-naive baseline |
| POST | `/forecast/ml` | Recursive random-forest forecast |
| POST | `/forecast/backtest` | Chronological holdout predictions |
| POST | `/forecast/compare` | Compare baseline and ML metrics |
| POST | `/forecast/batch` | Forecast multiple SKU histories |
| POST | `/inventory/recommendation` | Safety stock and suggested order |
| POST | `/inventory/risk` | Stockout / healthy / overstock classification |

## Example: persist sales observations

```json
{
  "observations": [
    {"sku": "SKU-100", "sales_date": "2026-01-01", "units_sold": 12},
    {"sku": "SKU-100", "sales_date": "2026-01-02", "units_sold": 15}
  ]
}
```

Send this payload to `POST /sales/observations`. Repeating the same SKU/date updates that observation rather than creating a duplicate. Dates are validated as ISO calendar dates; each request accepts up to 5,000 rows. The database is SQLite by default at `data/demandiq.db`; set `DEMANDIQ_DB_PATH` to change its location. Use `GET /sales/skus` and `GET /sales/{sku}/history` to inspect saved data.

## Example: machine-learning forecast

```json
{
  "history": [10, 12, 11, 9, 14, 16, 13, 10, 12, 11, 9, 15, 17, 14, 11, 13, 12, 10, 16, 18, 15, 12, 14, 13, 11, 17, 19, 16],
  "horizon": 7
}
```

The ML forecaster requires at least eight observations. The chronological model comparison requires at least 22 training observations in addition to its holdout horizon. Inputs are daily unit-demand values in chronological order.

## Example: replenishment recommendation

```json
{
  "forecast": [12, 14, 13, 11, 15, 16, 14],
  "on_hand": 35,
  "lead_time_days": 5,
  "service_factor": 1.65,
  "review_period_days": 0
}
```

The recommendation is a transparent heuristic using forecast mean, forecast variability, lead time, and current on-hand stock. It does not include inbound purchase orders or allocated stock; do not interpret it as a complete inventory position.
