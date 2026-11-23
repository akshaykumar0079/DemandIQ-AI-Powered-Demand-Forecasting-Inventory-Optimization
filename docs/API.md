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
| POST | `/forecast/baseline` | Seasonal-naive baseline |
| POST | `/forecast/ml` | Recursive random-forest forecast |
| POST | `/forecast/backtest` | Chronological holdout predictions |
| POST | `/forecast/compare` | Compare baseline and ML metrics |
| POST | `/forecast/batch` | Forecast multiple SKU histories |
| POST | `/inventory/recommendation` | Safety stock and suggested order |
| POST | `/inventory/risk` | Stockout / healthy / overstock classification |

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
