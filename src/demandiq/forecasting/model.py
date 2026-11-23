"""Machine-learning forecasting model with recursive multi-step prediction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from demandiq.forecasting.features import build_training_frame, next_day_features


@dataclass
class DemandForecaster:
    """Random-forest model using recent demand lags and calendar position."""

    n_estimators: int = 200
    random_state: int = 42

    def __post_init__(self) -> None:
        if self.n_estimators < 10:
            raise ValueError("n_estimators must be at least 10.")
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=8,
            min_samples_leaf=2,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self._fitted = False
        self._history: list[float] = []

    def fit(self, history: list[float]) -> DemandForecaster:
        """Fit the model on an ordered daily demand history."""
        features, target = build_training_frame(history)
        self.model.fit(features, target)
        self._history = [float(value) for value in history]
        self._fitted = True
        return self

    def predict(self, horizon: int) -> list[float]:
        """Forecast multiple days recursively, clipping impossible negative demand."""
        if not self._fitted:
            raise RuntimeError("Call fit() before predict().")
        if horizon < 1 or horizon > 365:
            raise ValueError("Horizon must be between 1 and 365 days.")
        history = self._history.copy()
        predictions: list[float] = []
        for _ in range(horizon):
            features = next_day_features(history, len(history))
            prediction = max(0.0, float(self.model.predict(features)[0]))
            predictions.append(prediction)
            history.append(prediction)
        return predictions


def chronological_backtest(history: list[float], horizon: int = 7) -> dict[str, object]:
    """Evaluate a single chronological holdout without shuffling observations."""
    values = np.asarray(history, dtype=float)
    if values.ndim != 1 or values.size < 22:
        raise ValueError("At least 22 observations are required for chronological backtesting.")
    if horizon < 1 or horizon >= values.size - 14:
        raise ValueError("Backtest horizon must leave at least 14 training observations.")
    train, actual = values[:-horizon], values[-horizon:]
    predictions = DemandForecaster().fit(train.tolist()).predict(horizon)
    return {"actual": actual.tolist(), "predicted": predictions}
