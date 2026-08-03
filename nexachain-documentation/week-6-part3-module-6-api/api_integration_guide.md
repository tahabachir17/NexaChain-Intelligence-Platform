# NexaChain Prediction API Integration Guide

## Integration contract

The target API is versioned under `http://localhost:8000/api/v1`. Every prediction operation uses `POST`, accepts a JSON body, and has no path or query parameters. The current code has no authentication middleware; production clients must not interpret that as approval for anonymous access.

> **Contract status matters.** Only working capital, cash flow, procurement cost, and profitability are registered and tested in this repository. Four additional contracts come from the continuity report but are not registered. Demand forecast and supplier score are proposed contracts supplied to complete the requested ten-endpoint reference; product and engineering approval is required before implementation.

### Common headers

```http
Content-Type: application/json
Accept: application/json
X-Correlation-ID: <uuid>   # recommended; not yet enforced
Authorization: Bearer <token>   # recommended for production; not implemented
```

### Common successful response

```json
{
  "status": "success",
  "model": "Model Name",
  "prediction": {},
  "timestamp": "2026-08-03T10:15:30Z"
}
```

Sample values below demonstrate valid shapes. They are not service-level guarantees or live predictions.

## 1. Demand Forecast

**Endpoint URL:** `/api/v1/predict/demand-forecast`  
**HTTP method:** `POST`  
**Repository status:** Proposed; not registered  
**Business description:** Forecasts product demand for a warehouse over a requested daily horizon to support replenishment and capacity planning.

**Parameters:** no path or query parameters; JSON body only.

| Body field | Type | Required | Rules |
|---|---|---:|---|
| `product_id` | string | yes | non-blank |
| `warehouse_id` | string | yes | non-blank |
| `forecast_horizon_days` | integer | yes | proposed range 1–90 |
| `history_end_date` | ISO date | yes | last observed demand date |
| `promotion_planned` | boolean | yes | known future promotion flag |

```json
{
  "product_id": "PROD-1042",
  "warehouse_id": "WH-07",
  "forecast_horizon_days": 30,
  "history_end_date": "2024-12-31",
  "promotion_planned": false
}
```

```json
{
  "status": "success",
  "model": "Demand Forecast",
  "prediction": {
    "forecast_horizon_days": 30,
    "total_forecast_units": 1840.0,
    "average_daily_demand": 61.33,
    "lower_bound_units": 1560.0,
    "upper_bound_units": 2135.0
  },
  "timestamp": "2026-08-03T10:15:30Z"
}
```

**Errors and status codes:** `200` proposed success; `400` invalid identifier/date/horizon; `401/403` future security; `422` possible conventional schema response until normalized; `500` model-output/internal failure; `503` model unavailable. Current behavior is `404` because the route is not registered.

**Authentication:** none in current code; Bearer token with `predict:demand` scope is recommended.

## 2. Delivery Delay Prediction

**Endpoint URL:** `/api/v1/predict/delivery-delay`  
**HTTP method:** `POST`  
**Repository status:** Specified in continuity report; not registered  
**Business description:** Estimates the probability and expected duration of a delivery delay for proactive customer and carrier intervention.

**Parameters:** no path or query parameters; all body fields are required: `carrier_id` (string), `route_id` (string), `carrier_type` (string), `shipment_weight` (non-negative number), `origin` (string), `destination` (string), and `customs_clearance_days` (non-negative number).

```json
{
  "carrier_id": "CAR-021",
  "route_id": "RTE-00150",
  "carrier_type": "Ocean",
  "shipment_weight": 12450.5,
  "origin": "Casablanca",
  "destination": "Rotterdam",
  "customs_clearance_days": 2.0
}
```

```json
{
  "status": "success",
  "model": "Delivery Delay Prediction",
  "prediction": {
    "delay_probability": 0.35,
    "expected_delay_days": 2.1,
    "risk_category": "Moderate"
  },
  "timestamp": "2026-08-03T10:16:00Z"
}
```

**Errors and status codes:** `200` specified success; `400` missing/invalid route, weight, or customs duration; `401/403` future security; `422` possible conventional schema response; `500` inference failure; `503` model unavailable. Current route response: `404`.

**Authentication:** none implemented; Bearer token with `predict:logistics` scope recommended.

## 3. Vendor Risk Prediction

**Endpoint URL:** `/api/v1/predict/vendor-risk`  
**HTTP method:** `POST`  
**Repository status:** Specified in continuity report; not registered  
**Business description:** Converts delivery, quality, stability, and concentration indicators into a vendor risk assessment and sourcing action.

**Parameters:** body only. Required fields are `vendor_id` (non-blank string), `on_time_delivery_rate`, `quality_acceptance_rate`, `financial_stability_score`, and `concentration_risk_percentage` (numbers; scales must be finalized as 0–1 or 0–100 before implementation).

```json
{
  "vendor_id": "VEN-0108",
  "on_time_delivery_rate": 92.4,
  "quality_acceptance_rate": 97.8,
  "financial_stability_score": 71.0,
  "concentration_risk_percentage": 18.5
}
```

```json
{
  "status": "success",
  "model": "Vendor Risk Prediction",
  "prediction": {
    "vendor_risk_score": 28.5,
    "risk_classification": "Moderate",
    "recommendation": "Monitor delivery and concentration exposure"
  },
  "timestamp": "2026-08-03T10:16:30Z"
}
```

**Errors and status codes:** `200` specified success; `400` blank vendor or out-of-scale metric; `401/403` future security; `422` possible schema failure; `500` inference failure; `503` unavailable model; current `404` because unregistered.

**Authentication:** none implemented; Bearer token with `predict:supplier-risk` scope recommended.

## 4. Stockout Prediction

**Endpoint URL:** `/api/v1/predict/stockout`  
**HTTP method:** `POST`  
**Repository status:** Specified in continuity report; not registered  
**Business description:** Predicts near-term stockout probability and recommends a replenishment quantity for a product-location pair.

**Parameters:** body only. Required: `product_id` and `warehouse_id` (non-blank strings), `stock_on_hand` (integer ≥ 0), `days_of_supply`, `lead_time`, and `average_demand` (numbers ≥ 0).

```json
{
  "product_id": "PROD-1042",
  "warehouse_id": "WH-07",
  "stock_on_hand": 125,
  "days_of_supply": 3.2,
  "lead_time": 9.0,
  "average_demand": 39.0
}
```

```json
{
  "status": "success",
  "model": "Inventory Stockout Prediction",
  "prediction": {
    "stockout_probability": 0.82,
    "recommended_reorder_quantity": 500,
    "risk_level": "High"
  },
  "timestamp": "2026-08-03T10:17:00Z"
}
```

**Errors and status codes:** `200` specified success; `400` negative inventory or demand inputs; `401/403` future security; `422` possible schema failure; `500` inference failure; `503` model unavailable; current `404` because unregistered.

**Authentication:** none implemented; Bearer token with `predict:inventory` scope recommended.

## 5. Working Capital Forecast

**Endpoint URL:** `/api/v1/predict/working-capital`  
**HTTP method:** `POST`  
**Repository status:** Implemented and contract-tested  
**Business description:** Forecasts working capital for an inclusive date period and returns the expected liquidity direction and confidence.

**Parameters:** body only. All fields required.

| Field | Type | Validation |
|---|---|---|
| `period_start` | ISO date | valid date |
| `period_end` | ISO date | on or after start |
| `accounts_receivable_balance` | number | ≥ 0, finite |
| `accounts_payable_balance` | number | ≥ 0, finite |
| `inventory_value` | number | ≥ 0, finite |

```json
{
  "period_start": "2026-07-01",
  "period_end": "2026-07-31",
  "accounts_receivable_balance": 500000,
  "accounts_payable_balance": 200000,
  "inventory_value": 100000
}
```

```json
{
  "status": "success",
  "model": "Working Capital Forecast",
  "prediction": {
    "forecasted_working_capital": 400000.0,
    "liquidity_trend": "improving",
    "confidence_score": 0.91
  },
  "timestamp": "2026-08-03T10:17:30Z"
}
```

**Errors and status codes:** `200` success; `400` missing/invalid fields, extra fields, negative balances, or reversed dates; `500` invalid model output/unexpected failure; `503` model not configured/load failure. The exception handler normalizes request validation to `400`, although generated OpenAPI may also advertise `422`.

```json
{"status":"error","message":"period_end is required.","error_code":400}
```

**Authentication:** none implemented; Bearer token with `predict:finance` scope recommended.

## 6. Cash Flow Forecast

**Endpoint URL:** `/api/v1/predict/cash-flow`  
**HTTP method:** `POST`  
**Repository status:** Implemented and contract-tested  
**Business description:** Produces a 1–52 week cash-flow path and a financial-health signal for treasury planning.

**Parameters:** body only. `forecast_weeks` is an integer from 1 to 52; `current_cash_position`, `outstanding_payables`, and `expected_receivables` are required finite numbers ≥ 0.

```json
{
  "forecast_weeks": 3,
  "current_cash_position": 1000000,
  "outstanding_payables": 250000,
  "expected_receivables": 400000
}
```

```json
{
  "status": "success",
  "model": "Cash Flow Forecast",
  "prediction": {
    "cash_flow_forecast": [1150000.0, 1175000.0, 1200000.0],
    "weekly_trend": [
      {"week": 1, "predicted_cash_flow": 1150000.0},
      {"week": 2, "predicted_cash_flow": 1175000.0},
      {"week": 3, "predicted_cash_flow": 1200000.0}
    ],
    "financial_health_indicator": "healthy"
  },
  "timestamp": "2026-08-03T10:18:00Z"
}
```

**Errors and status codes:** `200` success; `400` horizon outside 1–52, negative values, missing or extra fields; `500` invalid model response/internal failure; `503` model unavailable. Runtime request validation is normalized to `400`; OpenAPI may list `422`.

```json
{"status":"error","message":"The requested model is currently unavailable.","error_code":503}
```

**Authentication:** none implemented; Bearer token with `predict:finance` scope recommended.

## 7. Procurement Cost Prediction

**Endpoint URL:** `/api/v1/predict/procurement-cost`  
**HTTP method:** `POST`  
**Repository status:** Implemented and contract-tested  
**Business description:** Estimates total procurement cost, a plausible range, and a suggested purchasing window under current market conditions.

**Parameters:** body only. All fields required. `product_category` must be `Precision`, `Industrial`, `Electronics`, or `Raw Materials`; `market_conditions` must be `stable`, `volatile`, `rising`, or `falling`; `quantity` > 0; `lead_time` is an integer ≥ 0.

```json
{
  "vendor_id": "VEN-100",
  "product_category": "Industrial",
  "quantity": 10,
  "lead_time": 7,
  "market_conditions": "stable"
}
```

```json
{
  "status": "success",
  "model": "Procurement Cost Prediction",
  "prediction": {
    "estimated_procurement_cost": 125.0,
    "cost_range": {"min": 112.5, "max": 137.5},
    "suggested_procurement_window": "within 14 days"
  },
  "timestamp": "2026-08-03T10:18:30Z"
}
```

**Errors and status codes:** `200` success; `400` invalid enum, blank vendor, non-positive quantity, negative lead time, missing or extra field; `500` invalid model output/internal error; `503` unavailable model. Runtime schema failures are `400`; OpenAPI may also show `422`.

**Authentication:** none implemented; Bearer token with `predict:procurement` scope recommended.

## 8. Profitability Prediction

**Endpoint URL:** `/api/v1/predict/profitability`  
**HTTP method:** `POST`  
**Repository status:** Implemented and contract-tested  
**Business description:** Estimates expected profit, profit-margin percentage, and profitability category for a proposed sale.

**Parameters:** body only. `product`, `vendor`, and `customer` are required non-blank strings; `quantity` is an integer > 0; `sales_channel` is `online`, `retail`, `wholesale`, or `direct`.

```json
{
  "product": "PROD-1",
  "vendor": "VEN-1",
  "customer": "CUST-1",
  "quantity": 5,
  "sales_channel": "online"
}
```

```json
{
  "status": "success",
  "model": "Profitability Prediction",
  "prediction": {
    "expected_profit": 40.0,
    "profit_margin": 24.5,
    "profitability_category": "high"
  },
  "timestamp": "2026-08-03T10:19:00Z"
}
```

**Errors and status codes:** `200` success; `400` blank identifiers, invalid channel, non-positive quantity, missing or extra field; `500` invalid model output/internal error; `503` unavailable model. Runtime validation is `400`; OpenAPI may list `422`.

**Authentication:** none implemented; Bearer token with `predict:commercial` scope recommended.

## 9. Route Risk Evaluation

**Endpoint URL:** `/api/v1/predict/route-risk`  
**HTTP method:** `POST`  
**Repository status:** Specified in continuity report; not registered  
**Business description:** Scores route-level logistics risk and proposes an alternative route when exposure is elevated.

**Parameters:** body only. Required fields: `origin`, `destination`, and `carrier_type` (non-blank strings), `shipment_weight` (number ≥ 0), and `departure_date` (ISO date).

```json
{
  "origin": "Casablanca",
  "destination": "Rotterdam",
  "carrier_type": "Ocean",
  "shipment_weight": 12450.5,
  "departure_date": "2026-08-10"
}
```

```json
{
  "status": "success",
  "model": "Route Risk Prediction",
  "prediction": {
    "route_risk_score": 25.0,
    "expected_delay": 0.5,
    "alternative_route_recommendation": "RTE-00150"
  },
  "timestamp": "2026-08-03T10:19:30Z"
}
```

**Errors and status codes:** `200` specified success; `400` invalid location, weight, or date; `401/403` future security; `422` possible schema failure; `500` inference failure; `503` model unavailable; current `404` because unregistered.

**Authentication:** none implemented; Bearer token with `predict:logistics` scope recommended.

## 10. Supplier Composite Score

**Endpoint URL:** `/api/v1/predict/supplier-score`  
**HTTP method:** `POST`  
**Repository status:** Proposed; not registered  
**Business description:** Produces a versioned composite supplier score aligned with delivery, quality, risk, cost-efficiency, and lead-time performance.

**Parameters:** body only. Proposed required fields are `vendor_id` (non-blank), `as_of_date` (ISO date), `on_time_delivery_rate`, `quality_acceptance_rate`, `risk_performance_score`, `cost_efficiency_score`, and `lead_time_score` (finite 0–100 values).

```json
{
  "vendor_id": "VEN-0108",
  "as_of_date": "2024-12-31",
  "on_time_delivery_rate": 92.4,
  "quality_acceptance_rate": 97.8,
  "risk_performance_score": 74.0,
  "cost_efficiency_score": 81.5,
  "lead_time_score": 88.0
}
```

```json
{
  "status": "success",
  "model": "Supplier Composite Score",
  "prediction": {
    "supplier_score": 87.33,
    "score_band": "Strategic",
    "component_scores": {
      "delivery": 92.4,
      "quality": 97.8,
      "risk_performance": 74.0,
      "cost_efficiency": 81.5,
      "lead_time": 88.0
    },
    "recommended_action": "Eligible for strategic-partner review"
  },
  "timestamp": "2026-08-03T10:20:00Z"
}
```

The example uses the documented score weights: 30%, 20%, 20%, 15%, and 15% respectively.

**Errors and status codes:** `200` proposed success; `400` invalid date or score outside 0–100; `401/403` future security; `422` possible schema failure; `500` scoring/internal failure; `503` unavailable model; current `404` because unregistered.

**Authentication:** none implemented; Bearer token with `predict:supplier-score` scope recommended.

## Client implementation pattern

```python
import requests

response = requests.post(
    "https://api.example.com/api/v1/predict/working-capital",
    headers={"Authorization": "Bearer <token>", "X-Correlation-ID": "<uuid>"},
    json={
        "period_start": "2026-07-01",
        "period_end": "2026-07-31",
        "accounts_receivable_balance": 500000,
        "accounts_payable_balance": 200000,
        "inventory_value": 100000,
    },
    timeout=10,
)
response.raise_for_status()
prediction = response.json()["prediction"]
```

Clients should retry only `429`, transient `500`, and `503` responses, with exponential backoff, jitter, a maximum attempt count, and an end-to-end deadline. Do not retry `400`, `401`, `403`, `404`, or `422` unchanged.

## Production acceptance checklist

- All ten routes registered in `/openapi.json` with approved schemas.
- Authentication, authorization scopes, TLS, rate limits, and audit logs enabled.
- Model name, immutable version, correlation ID, and feature timestamp returned.
- Contract, integration, load, security, and rollback tests passed.
- Monitoring covers latency, errors, availability, input drift, output drift, and business outcomes.
- Example payloads are replayed as smoke tests and contain no confidential data.
