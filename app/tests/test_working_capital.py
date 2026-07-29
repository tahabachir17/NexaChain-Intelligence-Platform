import pytest

URL = "/api/v1/predict/working-capital"
VALID_PAYLOAD = {
    "period_start": "2026-07-01",
    "period_end": "2026-07-31",
    "accounts_receivable_balance": 500_000,
    "accounts_payable_balance": 200_000,
    "inventory_value": 100_000,
}


def test_valid_working_capital_prediction(client):
    response = client.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["model"] == "Working Capital Forecast"
    assert body["prediction"] == {
        "forecasted_working_capital": 400_000.0,
        "liquidity_trend": "improving",
        "confidence_score": 0.91,
    }
    assert body["timestamp"].endswith("Z")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("period_start", "July 1, 2026"),
        ("accounts_receivable_balance", -1),
        ("accounts_payable_balance", -1),
        ("inventory_value", -1),
    ],
)
def test_invalid_working_capital_values(client, field, value):
    response = client.post(URL, json={**VALID_PAYLOAD, field: value})
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["error_code"] == 400


@pytest.mark.parametrize("missing_field", list(VALID_PAYLOAD))
def test_missing_working_capital_fields(client, missing_field):
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != missing_field}
    response = client.post(URL, json=payload)
    assert response.status_code == 400
    assert response.json()["message"] == f"{missing_field} is required."


def test_period_end_cannot_precede_start(client):
    response = client.post(URL, json={**VALID_PAYLOAD, "period_end": "2026-06-30"})
    assert response.status_code == 400
    assert "period_end" in response.json()["message"]


def test_zero_balances_and_same_day_period_are_accepted(client):
    payload = {
        **VALID_PAYLOAD,
        "period_end": VALID_PAYLOAD["period_start"],
        "accounts_receivable_balance": 0,
        "accounts_payable_balance": 0,
        "inventory_value": 0,
    }
    assert client.post(URL, json=payload).status_code == 200
