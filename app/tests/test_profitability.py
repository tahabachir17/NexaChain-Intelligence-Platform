import pytest

URL = "/api/v1/predict/profitability"
VALID_PAYLOAD = {
    "product": "PROD-1",
    "vendor": "VEN-1",
    "customer": "CUST-1",
    "quantity": 5,
    "sales_channel": "online",
}


def test_valid_profitability_prediction(client):
    response = client.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["model"] == "Profitability Prediction"
    assert body["prediction"] == {
        "expected_profit": 40.0,
        "profit_margin": 24.5,
        "profitability_category": "high",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("product", ""),
        ("vendor", "   "),
        ("customer", ""),
        ("quantity", 0),
        ("sales_channel", "marketplace"),
    ],
)
def test_invalid_profitability_values(client, field, value):
    response = client.post(URL, json={**VALID_PAYLOAD, field: value})
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert field in response.json()["message"]


@pytest.mark.parametrize("missing_field", list(VALID_PAYLOAD))
def test_missing_profitability_fields(client, missing_field):
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != missing_field}
    response = client.post(URL, json=payload)
    assert response.status_code == 400
    assert response.json()["message"] == f"{missing_field} is required."


def test_minimum_quantity_and_each_sales_channel_are_accepted(client):
    for channel in ("online", "retail", "wholesale", "direct"):
        response = client.post(URL, json={**VALID_PAYLOAD, "quantity": 1, "sales_channel": channel})
        assert response.status_code == 200
