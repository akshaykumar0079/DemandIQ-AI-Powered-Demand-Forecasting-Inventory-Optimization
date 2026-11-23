# DemandIQ — AI-Powered Demand Forecasting & Inventory Optimization

DemandIQ is a portfolio-grade demand planning application that turns historical product sales into interpretable forecasts and practical replenishment recommendations. It is designed for small retail and warehouse teams that need to anticipate demand, understand forecast quality, and reduce avoidable stockouts and excess inventory.

## What it will do

- Validate and aggregate daily sales history by SKU.
- Train and compare forecasting baselines (seasonal naive and machine-learning regression).
- Generate daily forecasts with backtesting metrics (MAE, RMSE, sMAPE).
- Estimate safety stock, reorder points, and suggested order quantities from forecast demand and lead time.
- Expose forecasts and recommendations through a FastAPI service.
- Provide a React dashboard for product-level planning and model evaluation.

## Architecture

```text
CSV / database
     |
     v
Data validation + daily aggregation
     |
     v
Feature engineering --> chronological backtesting --> model selection
     |                                               |
     v                                               v
Forecast service ------------------------------> Forecast metrics
     |
     v
Inventory policy (lead time, service level, on-hand)
     |
     v
FastAPI --> React dashboard
```

## Current development status

The repository is being built incrementally. The initial milestone establishes the Python package, validated sales-data contract, forecasting primitives, and automated tests. API, persistence, dashboard, and deployment layers will be added in later milestones. Do not treat planned features as implemented until they appear in the code and tests.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
pytest
```

## Sales CSV contract

The minimum input columns are:

| Column | Meaning |
| --- | --- |
| `date` | Sales date in ISO format (YYYY-MM-DD) |
| `sku` | Stable product identifier |
| `quantity` | Non-negative units sold |

Optional columns such as `price` and `store_id` may be retained by downstream integrations. Missing dates are not automatically interpreted as zero sales; callers should define the observation calendar before forecasting.

## Development commands

```bash
ruff check .
ruff format --check .
pytest
```

## Responsible use and limitations

Forecasts are estimates, not guarantees. New products, promotions, holidays, stockouts, price changes, and supply disruptions can make historical patterns unreliable. Inventory recommendations depend on the supplied lead time, service level, and stock position. Review recommendations before placing orders.

This is an educational portfolio project, not a production inventory control system. Production deployment would require authentication, authorization, managed secrets, database migrations, observability, backups, and operational validation.
