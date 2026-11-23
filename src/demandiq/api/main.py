"""FastAPI application exposing DemandIQ's first planning endpoints."""

from __future__ import annotations

import os
from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from demandiq.data.sqlite_store import SalesObservation, SalesStore
from demandiq.forecasting.baseline import seasonal_naive
from demandiq.forecasting.batch import forecast_skus
from demandiq.forecasting.evaluation import compare_forecasters
from demandiq.forecasting.model import DemandForecaster, chronological_backtest
from demandiq.inventory.policy import recommend_replenishment
from demandiq.inventory.risk import classify_inventory_risk

app = FastAPI(
    title="DemandIQ API",
    description="Demand forecasting and inventory replenishment planning.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# Override DEMANDIQ_DB_PATH to place the SQLite file outside the project directory.
sales_store = SalesStore(os.getenv("DEMANDIQ_DB_PATH", "data/demandiq.db"))


class SalesObservationInput(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    sales_date: date
    units_sold: float = Field(ge=0)


class SalesBatchRequest(BaseModel):
    observations: list[SalesObservationInput] = Field(min_length=1, max_length=5000)


class ForecastRequest(BaseModel):
    history: list[float] = Field(min_length=1)
    horizon: int = Field(default=7, ge=1, le=365)
    season_length: int = Field(default=7, ge=1, le=90)


class ReplenishmentRequest(BaseModel):
    forecast: list[float] = Field(min_length=1)
    on_hand: int = Field(ge=0)
    lead_time_days: int = Field(ge=0)
    service_factor: float = Field(default=1.65, ge=0)
    review_period_days: int = Field(default=0, ge=0)
    on_order: int = Field(default=0, ge=0)
    allocated: int = Field(default=0, ge=0)


class BatchForecastRequest(BaseModel):
    histories: dict[str, list[float]] = Field(min_length=1)
    horizon: int = Field(default=7, ge=1, le=365)


class InventoryRiskRequest(BaseModel):
    on_hand: int = Field(ge=0)
    reorder_point: int = Field(ge=0)
    target_stock: int = Field(ge=0)


@app.get("/health")
def health() -> dict[str, str]:
    """Basic process health endpoint."""
    return {"status": "ok", "service": "DemandIQ"}


@app.post("/sales/observations")
def save_sales_observations(request: SalesBatchRequest) -> dict[str, int]:
    """Persist daily sales observations, upserting duplicate SKU/date pairs."""
    observations = [
        SalesObservation(
            sku=item.sku.strip(),
            date=item.sales_date.isoformat(),
            units_sold=item.units_sold,
        )
        for item in request.observations
    ]
    try:
        saved = sales_store.upsert_many(observations)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"saved": saved}


@app.get("/sales/skus")
def list_sales_skus() -> dict[str, list[str]]:
    """List all SKU identifiers with stored sales history."""
    return {"skus": sales_store.skus()}


@app.get("/sales/{sku}/history")
def get_sales_history(sku: str) -> dict[str, object]:
    """Return persisted daily sales observations for one SKU."""
    observations = sales_store.history(sku)
    return {
        "sku": sku,
        "observations": [
            {"date": item.date, "units_sold": item.units_sold}
            for item in observations
        ],
    }


@app.post("/forecast/batch")
def forecast_batch(request: BatchForecastRequest) -> dict[str, object]:
    """Forecast multiple SKUs in one request."""
    try:
        return {"forecasts": forecast_skus(request.histories, request.horizon)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/forecast/baseline")
def forecast_baseline(request: ForecastRequest) -> dict[str, object]:
    """Return a transparent seasonal-naive forecast."""
    try:
        values = seasonal_naive(request.history, request.horizon, request.season_length)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"method": "seasonal_naive", "forecast": values, "horizon": request.horizon}


@app.post("/forecast/ml")
def forecast_ml(request: ForecastRequest) -> dict[str, object]:
    """Return a recursive random-forest forecast for sufficiently long history."""
    try:
        values = DemandForecaster().fit(request.history).predict(request.horizon)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"method": "random_forest_lag_features", "forecast": values, "horizon": request.horizon}


@app.post("/forecast/backtest")
def forecast_backtest(request: ForecastRequest) -> dict[str, object]:
    """Evaluate a chronological holdout using the machine-learning forecaster."""
    try:
        result = chronological_backtest(request.history, request.horizon)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result


@app.post("/forecast/compare")
def forecast_compare(request: ForecastRequest) -> dict[str, object]:
    """Compare seasonal-naive and random-forest candidates chronologically."""
    try:
        return compare_forecasters(request.history, request.horizon)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/inventory/risk")
def inventory_risk(request: InventoryRiskRequest) -> dict[str, object]:
    """Classify stockout or overstock exposure against policy thresholds."""
    try:
        return classify_inventory_risk(
            on_hand=request.on_hand,
            reorder_point=request.reorder_point,
            target_stock=request.target_stock,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/inventory/recommendation")
def inventory_recommendation(request: ReplenishmentRequest) -> dict[str, object]:
    """Return reorder point and suggested order quantity."""
    try:
        result = recommend_replenishment(
            request.forecast,
            on_hand=request.on_hand,
            lead_time_days=request.lead_time_days,
            service_factor=request.service_factor,
            review_period_days=request.review_period_days,
            on_order=request.on_order,
            allocated=request.allocated,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result.__dict__
