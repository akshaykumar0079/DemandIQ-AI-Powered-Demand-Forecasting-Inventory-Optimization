from fastapi.testclient import TestClient

from demandiq.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_baseline_forecast_endpoint():
    response = client.post("/forecast/baseline", json={
        "history":[4,5,6,7,8,9,10],"horizon":3,"season_length":7
    })
    assert response.status_code == 200
    assert response.json()["forecast"] == [4,5,6]


def test_forecast_endpoint_rejects_empty_history():
    response = client.post("/forecast/baseline", json={"history":[],"horizon":3})
    assert response.status_code == 422


def test_inventory_recommendation_endpoint():
    response = client.post("/inventory/recommendation", json={
        "forecast":[5,5,5,5],"on_hand":2,"lead_time_days":2
    })
    assert response.status_code == 200
    assert response.json()["reorder_point"] == 10
    assert response.json()["suggested_order_quantity"] >= 0


def test_machine_learning_forecast_endpoint():
    history = [float(5 + index % 5) for index in range(35)]
    response = client.post("/forecast/ml", json={"history":history,"horizon":3})
    assert response.status_code == 200
    assert response.json()["method"] == "random_forest_lag_features"
    assert len(response.json()["forecast"]) == 3


def test_backtest_endpoint_returns_holdout_predictions():
    history = [float(5 + index % 5) for index in range(35)]
    response = client.post("/forecast/backtest", json={"history":history,"horizon":5})
    assert response.status_code == 200
    assert len(response.json()["actual"]) == 5
    assert len(response.json()["predicted"]) == 5

def test_forecast_comparison_endpoint():
    history = [float(8 + index % 7) for index in range(42)]
    response = client.post("/forecast/compare", json={"history":history,"horizon":7})
    assert response.status_code == 200
    assert set(response.json()["models"]) == {"seasonal_naive", "random_forest"}
    assert response.json()["recommended_model"] in response.json()["models"]
