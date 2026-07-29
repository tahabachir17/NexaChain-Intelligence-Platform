import pytest

URL = "/api/v1/predict/procurement-cost"
VALID_PAYLOAD = {
    "vendor_id": "VEN-100",
    "product_category": "Industrial",
    "quantity": 10,
    "lead_time": 7,
    "market_conditions": "stable",
}


def test_valid_procurement_cost_prediction(client):
    response = client.post(URL, json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["model"] == "Procurement Cost Prediction"
    assert body["prediction"]["estimated_procurement_cost"] == 125.0
    assert body["prediction"]["cost_range"] == {"min": 112.5, "max": 137.5}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("vendor_id", "   "),
        ("product_category", "unknown"),
        ("quantity", 0),
        ("lead_time", -1),
        ("market_conditions", "chaotic"),
    ],
)
def test_invalid_procurement_values(client, field, value):
    response = client.post(URL, json={**VALID_PAYLOAD, field: value})
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert field in response.json()["message"]


@pytest.mark.parametrize("missing_field", list(VALID_PAYLOAD))
def test_missing_procurement_fields(client, missing_field):
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != missing_field}
    response = client.post(URL, json=payload)
    assert response.status_code == 400
    assert response.json()["message"] == f"{missing_field} is required."


def test_minimum_quantity_and_zero_lead_time_are_accepted(client):
    response = client.post(URL, json={**VALID_PAYLOAD, "quantity": 1, "lead_time": 0})
    assert response.status_code == 200
