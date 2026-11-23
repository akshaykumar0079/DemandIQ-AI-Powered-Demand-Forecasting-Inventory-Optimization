"""FastAPI application exposing DemandIQ's first planning endpoints."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from demandiq.forecasting.baseline import seasonal_naive
from demandiq.forecasting.evaluation import compare_forecasters
from demandiq.forecasting.model import DemandForecaster, chronological_backtest
from demandiq.inventory.policy import recommend_replenishment

app = FastAPI(
    title="DemandIQ API",
    description="Demand forecasting and inventory replenishment planning.",
    version="0.1.0",
)


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


@app.get("/health")
def health() -> dict[str, str]:
    """Basic process health endpoint."""
    return {"status": "ok", "service": "DemandIQ"}


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
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result.__dict__
