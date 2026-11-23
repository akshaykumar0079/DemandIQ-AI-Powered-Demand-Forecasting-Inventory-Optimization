# DemandIQ — AI-Powered Demand Forecasting & Inventory Optimization

DemandIQ is an AI-assisted demand planning application that turns historical product sales into interpretable forecasts and practical replenishment recommendations. It combines a Python forecasting service, FastAPI endpoints, and a React dashboard.

## Features

- Validates and aggregates daily SKU sales from CSV files.
- Compares a seasonal-naive benchmark with a Random Forest model using lag, rolling-mean, weekday, and trend features.
- Generates recursive daily forecasts and chronological holdout predictions.
- Evaluates models with MAE, RMSE, and sMAPE; includes expanding-window rolling backtesting.
- Forecasts multiple SKUs in one request.
- Calculates safety stock, reorder points, target stock, and suggested order quantities.
- Accounts for on-hand, inbound, and allocated stock when calculating inventory position.
- Classifies stockout exposure, healthy stock, and overstock exposure.
- Persists daily SKU sales observations in SQLite with safe parameterized queries and idempotent SKU/date upserts.
- Provides FastAPI endpoints and a responsive React planning dashboard.
- Includes automated backend tests, frontend production build checks, and Docker Compose setup.

## Architecture

```text
CSV sales data
     |
     v
Validation + daily SKU aggregation
     |
     v
Lag / rolling / calendar features
     |
     v
Seasonal-naive baseline <--> Random Forest forecaster
     |                              |
     +------ chronological evaluation
                    |
                    v
         Forecast + error metrics
                    |
                    v
   Reorder point / safety stock / risk
                    |
                    v
             FastAPI service
                    |
                    v
          React planning dashboard
```

See [architecture notes](docs/ARCHITECTURE.md), [API reference](docs/API.md), and [development guide](docs/DEVELOPMENT.md).

## Quick start — backend

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
pytest
ruff check .
uvicorn demandiq.api.main:app --reload
```

API documentation: http://localhost:8000/docs

The API stores submitted sales observations in `data/demandiq.db` by default. Set `DEMANDIQ_DB_PATH` to use a different SQLite file. The sales-history endpoints are documented in [API reference](docs/API.md).

## Quick start — dashboard

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dashboard expects the API at http://localhost:8000 by default. Set `VITE_API_URL` to override it.

## Docker Compose

```bash
docker compose up --build
```

The API is exposed on port 8000 and the dashboard on port 5173.

## CSV demo

The minimum CSV columns are:

| Column | Meaning |
| --- | --- |
| `date` | Sales date in ISO format (YYYY-MM-DD) |
| `sku` | Stable product identifier |
| `quantity` | Non-negative whole units sold |

```bash
python scripts/demo.py data/sample_sales.csv --horizon 7
```

Missing dates are not automatically interpreted as zero sales. Define the observation calendar and stockout treatment before training on real business data.

## Quality checks

GitHub Actions runs Python lint and tests plus a TypeScript/Vite production build on pushes and pull requests to `main`.

## Responsible use and limitations

Forecasts are estimates, not guarantees. New products, promotions, holidays, stockouts, price changes, and supply disruptions can make historical patterns unreliable. The Random Forest implementation is a practical tabular baseline, not a claim of state-of-the-art accuracy. Recursive multi-step predictions can compound error.

Inventory calculations are transparent planning heuristics. They do not yet model supplier minimum order quantities, multiple supplier constraints, warehouse transfers, or a complete database-backed inventory ledger. Review recommendations before placing orders.

This is an educational portfolio project, not a production inventory control system. Production deployment would require authentication, authorization, managed secrets, database migrations, observability, backups, and operational validation.
