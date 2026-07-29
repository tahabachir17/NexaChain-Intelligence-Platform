from time import perf_counter

import pytest

from app.models.loader import (
    get_cash_flow_model,
    get_procurement_cost_model,
    get_profitability_model,
    get_working_capital_model,
)


ENDPOINT_CASES = [
    (
        "/api/v1/predict/working-capital",
        {
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "accounts_receivable_balance": 500_000,
            "accounts_payable_balance": 200_000,
            "inventory_value": 100_000,
        },
        "accounts_receivable_balance",
        [500_000],
    ),
    (
        "/api/v1/predict/cash-flow",
        {
            "forecast_weeks": 13,
            "current_cash_position": 1_000_000,
            "outstanding_payables": 250_000,
            "expected_receivables": 400_000,
        },
        "forecast_weeks",
        "thirteen",
    ),
    (
        "/api/v1/predict/procurement-cost",
        {
            "vendor_id": "VEN-100",
            "product_category": "Industrial",
            "quantity": 10,
            "lead_time": 7,
            "market_conditions": "stable",
        },
        "quantity",
        {"value": 10},
    ),
    (
        "/api/v1/predict/profitability",
        {
            "product": "PROD-1",
            "vendor": "VEN-1",
            "customer": "CUST-1",
            "quantity": 5,
            "sales_channel": "online",
        },
        "sales_channel",
        123,
    ),
]


@pytest.mark.parametrize(("url", "payload", "field", "invalid_value"), ENDPOINT_CASES)
def test_empty_payload_returns_standard_400(client, url, payload, field, invalid_value):
    response = client.post(url, json={})
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == "error"
    assert body["error_code"] == 400
    assert "required" in body["message"]


@pytest.mark.parametrize(("url", "payload", "field", "invalid_value"), ENDPOINT_CASES)
def test_invalid_data_types_return_standard_400(client, url, payload, field, invalid_value):
    response = client.post(url, json={**payload, field: invalid_value})
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == "error"
    assert body["error_code"] == 400
    assert field in body["message"]


@pytest.mark.parametrize(("url", "payload", "field", "invalid_value"), ENDPOINT_CASES)
def test_contract_layer_response_time_is_under_one_second(
    client, url, payload, field, invalid_value
):
    started = perf_counter()
    response = client.post(url, json=payload)
    elapsed_seconds = perf_counter() - started

    assert response.status_code == 200
    assert elapsed_seconds < 1.0


class RecordingModel:
    def __init__(self, output):
        self.output = output
        self.rows = None

    def predict(self, rows):
        self.rows = rows
        return self.output


PARITY_CASES = [
    (
        get_working_capital_model,
        ENDPOINT_CASES[0][0],
        ENDPOINT_CASES[0][1],
        {
            "forecasted_working_capital": 400_000.0,
            "liquidity_trend": "stable",
            "confidence_score": 0.88,
        },
    ),
    (
        get_cash_flow_model,
        ENDPOINT_CASES[1][0],
        {**ENDPOINT_CASES[1][1], "forecast_weeks": 2},
        {
            "cash_flow_forecast": [100.0, 125.0],
            "weekly_trend": [
                {"week": 1, "predicted_cash_flow": 100.0},
                {"week": 2, "predicted_cash_flow": 125.0},
            ],
            "financial_health_indicator": "healthy",
        },
    ),
    (
        get_procurement_cost_model,
        ENDPOINT_CASES[2][0],
        ENDPOINT_CASES[2][1],
        {
            "estimated_procurement_cost": 123.45,
            "cost_range": {"min": 120.0, "max": 130.0},
            "suggested_procurement_window": "within 14 days",
        },
    ),
    (
        get_profitability_model,
        ENDPOINT_CASES[3][0],
        ENDPOINT_CASES[3][1],
        {
            "expected_profit": -50.0,
            "profit_margin": -3.5,
            "profitability_category": "negative",
        },
    ),
]


@pytest.mark.parametrize(("dependency", "url", "payload", "model_output"), PARITY_CASES)
def test_api_prediction_matches_model_output(
    client, dependency, url, payload, model_output
):
    model = RecordingModel(model_output)
    client.app.dependency_overrides[dependency] = lambda: model

    response = client.post(url, json=payload)

    assert response.status_code == 200
    assert response.json()["prediction"] == model_output
    assert model.rows == [payload]
