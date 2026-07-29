# Week 6 Endpoint Testing Report

## 1. Executive result

The four prediction endpoints whose contracts were supplied passed the complete
automated API contract suite on 29 July 2026.

| Result | Value |
|---|---:|
| Automated tests | 69 passed |
| Failed tests | 0 |
| Runtime | 2.52 seconds |
| Warnings | 1 upstream `TestClient` deprecation warning |
| OpenAPI prediction routes verified | 4 |

The warning comes from the installed FastAPI/Starlette test client integration
and does not indicate an application or prediction failure.

Models 1–4, 9, and 10 cannot be tested or implemented until their endpoint
names, input schemas, output schemas, enum values, and model artifacts are
provided. This report does not represent those six undefined models as passed.

## 2. Test scope and environment

- Application: centralized FastAPI service under `app/`
- API prefix: `/api/v1`
- Automated runner: `pytest`
- In-process client: FastAPI `TestClient`
- Model isolation: deterministic injected model doubles
- Test command: `python -m pytest`
- Manual interfaces supported: Swagger UI, Postman, and cURL

Injected models make validation, routing, response formatting, and prediction
pass-through tests deterministic. They do not replace the required pre-release
integration run against the final MLflow artifacts.

## 3. Coverage matrix

| Test category | Working Capital | Cash Flow | Procurement Cost | Profitability |
|---|:---:|:---:|:---:|:---:|
| Valid prediction | Pass | Pass | Pass | Pass |
| Missing individual fields | Pass | Pass | Pass | Pass |
| Empty JSON object | Pass | Pass | Pass | Pass |
| Invalid data types | Pass | Pass | Pass | Pass |
| Invalid enum values | N/A input | Pass output | Pass | Pass |
| Numeric boundaries | Pass | Pass | Pass | Pass |
| Date format/order | Pass | N/A | N/A | N/A |
| Unknown fields | Shared strict schema | Pass | Shared strict schema | Shared strict schema |
| HTTP 200 success status | Pass | Pass | Pass | Pass |
| HTTP 400 validation status | Pass | Pass | Pass | Pass |
| Sanitized HTTP 503 | Shared handler | Pass | Shared handler | Shared handler |
| Standardized HTTP 404 | Pass (global) | Pass (global) | Pass (global) | Pass (global) |
| Contract response under 1 second | Pass | Pass | Pass | Pass |
| API prediction equals model output | Pass | Pass | Pass | Pass |
| Swagger/OpenAPI operation | Pass | Pass | Pass | Pass |

The one-second timing assertion measures FastAPI validation, dependency
resolution, serialization, and the deterministic model double. Production
latency must be measured again with the real model artifacts and deployment
hardware.

## 4. Sample functional requests and responses

The examples below use deterministic test-model outputs to demonstrate the API
contract. Production values will come from the configured MLflow models.

### 4.1 Working Capital Forecast

`POST /api/v1/predict/working-capital`

```json
{
  "period_start": "2026-07-01",
  "period_end": "2026-07-31",
  "accounts_receivable_balance": 500000,
  "accounts_payable_balance": 200000,
  "inventory_value": 100000
}
```

Sample HTTP 200 response:

```json
{
  "status": "success",
  "model": "Working Capital Forecast",
  "prediction": {
    "forecasted_working_capital": 400000.0,
    "liquidity_trend": "improving",
    "confidence_score": 0.91
  },
  "timestamp": "2026-07-29T16:00:00Z"
}
```

Boundary cases: zero balances and a same-day period are accepted. An end date
before the start date returns HTTP 400.

### 4.2 Cash Flow Forecast

`POST /api/v1/predict/cash-flow`

```json
{
  "forecast_weeks": 3,
  "current_cash_position": 1000000,
  "outstanding_payables": 250000,
  "expected_receivables": 400000
}
```

Sample HTTP 200 response:

```json
{
  "status": "success",
  "model": "Cash Flow Forecast",
  "prediction": {
    "cash_flow_forecast": [1000.0, 975.0, 950.0],
    "weekly_trend": [
      {"week": 1, "predicted_cash_flow": 1000.0},
      {"week": 2, "predicted_cash_flow": 975.0},
      {"week": 3, "predicted_cash_flow": 950.0}
    ],
    "financial_health_indicator": "healthy"
  },
  "timestamp": "2026-07-29T16:00:00Z"
}
```

Boundary cases: 1 and 52 weeks are accepted; 0 and 53 return HTTP 400.

### 4.3 Procurement Cost Prediction

`POST /api/v1/predict/procurement-cost`

```json
{
  "vendor_id": "VEN-100",
  "product_category": "Industrial",
  "quantity": 10,
  "lead_time": 7,
  "market_conditions": "stable"
}
```

Sample HTTP 200 response:

```json
{
  "status": "success",
  "model": "Procurement Cost Prediction",
  "prediction": {
    "estimated_procurement_cost": 125.0,
    "cost_range": {"min": 112.5, "max": 137.5},
    "suggested_procurement_window": "within 7 days"
  },
  "timestamp": "2026-07-29T16:00:00Z"
}
```

Boundary cases: quantity 1 and lead time 0 are accepted. Unknown product
categories and market conditions return HTTP 400.

### 4.4 Profitability Prediction

`POST /api/v1/predict/profitability`

```json
{
  "product": "PROD-1",
  "vendor": "VEN-1",
  "customer": "CUST-1",
  "quantity": 5,
  "sales_channel": "online"
}
```

Sample HTTP 200 response:

```json
{
  "status": "success",
  "model": "Profitability Prediction",
  "prediction": {
    "expected_profit": 40.0,
    "profit_margin": 24.5,
    "profitability_category": "high"
  },
  "timestamp": "2026-07-29T16:00:00Z"
}
```

Boundary cases: quantity 1 and every supported sales channel are accepted.
Blank identifiers, quantity 0, and unknown channels return HTTP 400.

## 5. Standard validation examples

Empty request:

```json
{}
```

Sample HTTP 400 response:

```json
{
  "status": "error",
  "message": "forecast_weeks is required.",
  "error_code": 400
}
```

Unavailable model, HTTP 503:

```json
{
  "status": "error",
  "message": "The requested model is currently unavailable.",
  "error_code": 503
}
```

No response exposes stack traces, internal exception details, or local paths.

## 6. Manual test procedure

Start the service from the repository root:

```powershell
uvicorn app.main:app --reload
```

Use Swagger at `http://127.0.0.1:8000/docs`, or import the OpenAPI document at
`http://127.0.0.1:8000/openapi.json` into Postman.

Example cURL request:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict/cash-flow" \
  -H "Content-Type: application/json" \
  -d '{"forecast_weeks":3,"current_cash_position":1000000,"outstanding_payables":250000,"expected_receivables":400000}'
```

## 7. Required MLflow integration gate

Before deployment, repeat the valid and latency cases with every final model URI
configured. For a fixed input fixture, call the loaded model directly and the
API, then compare the API `prediction` object with the model's output after JSON
serialization. Record model URI/version, input fixture, expected output, actual
output, latency percentile, and pass/fail status.

That integration gate is pending because loadable production model URIs were
not supplied. The automated parity tests currently prove that the API validates
and returns model output without applying undocumented prediction logic.
