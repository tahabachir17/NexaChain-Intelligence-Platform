import pytest

URL = "/api/v1/predict/cash-flow"
VALID_PAYLOAD = {
    "forecast_weeks": 3,
    "current_cash_position": 1_000_000,
    "outstanding_payables": 250_000,
    "expected_receivables": 400_000,
}


def test_valid_cash_flow_prediction(client):
    response = client.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["model"] == "Cash Flow Forecast"
    assert len(body["prediction"]["cash_flow_forecast"]) == 3
    assert len(body["prediction"]["weekly_trend"]) == 3
    assert body["prediction"]["financial_health_indicator"] == "healthy"
    assert body["timestamp"].endswith("Z")


@pytest.mark.parametrize(
    ("field", "value"),
    [("forecast_weeks", 0), ("forecast_weeks", 53), ("current_cash_position", -0.01),
     ("outstanding_payables", -1), ("expected_receivables", -1)],
)
def test_invalid_cash_flow_values_use_standard_error(client, field, value):
    response = client.post(URL, json={**VALID_PAYLOAD, field: value})
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["error_code"] == 400
    assert field in response.json()["message"]


@pytest.mark.parametrize("missing_field", list(VALID_PAYLOAD))
def test_missing_required_cash_flow_fields(client, missing_field):
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != missing_field}
    response = client.post(URL, json=payload)
    assert response.status_code == 400
    assert response.json() == {"status": "error", "message": f"{missing_field} is required.", "error_code": 400}


@pytest.mark.parametrize("weeks", [1, 52])
def test_forecast_week_boundaries_are_accepted(client, weeks):
    response = client.post(URL, json={**VALID_PAYLOAD, "forecast_weeks": weeks})
    assert response.status_code == 200
    assert len(response.json()["prediction"]["weekly_trend"]) == weeks


def test_unknown_fields_are_rejected(client):
    response = client.post(URL, json={**VALID_PAYLOAD, "secret_override": True})
    assert response.status_code == 400
    assert response.json()["error_code"] == 400


def test_unconfigured_model_returns_sanitized_503(client):
    client.app.dependency_overrides.clear()
    response = client.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 503
    assert response.json() == {"status": "error", "message": "The requested model is currently unavailable.", "error_code": 503}
    assert "URI" not in response.text
