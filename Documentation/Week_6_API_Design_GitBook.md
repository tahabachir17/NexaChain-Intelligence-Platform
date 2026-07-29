# ML Prediction API — Design and Usage

## Overview

The ML Prediction API is one centralized FastAPI application designed to serve
the project's MLflow models. A shared application gives every model the same
versioning, validation, response envelopes, error handling, documentation,
logging, and startup lifecycle.

Current API version: `v1`

Local base URL:

```text
http://127.0.0.1:8000/api/v1
```

Interactive documentation:

```text
http://127.0.0.1:8000/docs
```

## Design principles

1. **One service, multiple models.** Model routes are modules within one app,
   not independent FastAPI processes.
2. **Stable versioned URLs.** All prediction routes live below `/api/v1`.
3. **Schema-first contracts.** Each endpoint owns a dedicated Pydantic request
   and prediction schema.
4. **Models load once.** Configured MLflow models load during application
   startup and remain cached for requests.
5. **Safe failures.** Clients receive consistent, human-readable errors;
   diagnostic exception details remain in server logs.
6. **No environment-specific paths in code.** Model URIs and service settings
   come from environment variables.

## Request lifecycle

```text
Client
  → POST /api/v1/predict/<model-name>
  → Pydantic request validation
  → cached MLflow model lookup
  → model.predict(...)
  → prediction-schema validation
  → standardized success response
```

If any stage fails, a global handler returns the standardized error envelope
and logs the failure server-side.

## Standard response contracts

Success:

```json
{
  "status": "success",
  "model": "Model Display Name",
  "prediction": {},
  "timestamp": "2026-07-29T16:00:00Z"
}
```

Error:

```json
{
  "status": "error",
  "message": "A safe explanation for the client.",
  "error_code": 400
}
```

| HTTP status | Meaning |
|---:|---|
| 200 | Valid request and successful prediction |
| 400 | Missing, malformed, out-of-range, or unsupported input |
| 404 | Route does not exist |
| 500 | Unexpected service failure or invalid model output |
| 503 | Model is not configured or failed to load |

## Implemented endpoints

### Working Capital Forecast

```text
POST /api/v1/predict/working-capital
```

| Field | Type | Validation |
|---|---|---|
| `period_start` | ISO date | Required |
| `period_end` | ISO date | Required; not before start |
| `accounts_receivable_balance` | Number | Required; ≥ 0 |
| `accounts_payable_balance` | Number | Required; ≥ 0 |
| `inventory_value` | Number | Required; ≥ 0 |

Prediction fields: `forecasted_working_capital`, `liquidity_trend`, and
`confidence_score`. Confidence is restricted to 0–1.

### Cash Flow Forecast

```text
POST /api/v1/predict/cash-flow
```

| Field | Type | Validation |
|---|---|---|
| `forecast_weeks` | Integer | Required; 1–52 |
| `current_cash_position` | Number | Required; ≥ 0 |
| `outstanding_payables` | Number | Required; ≥ 0 |
| `expected_receivables` | Number | Required; ≥ 0 |

Prediction fields: `cash_flow_forecast`, `weekly_trend`, and
`financial_health_indicator`. Health values are `healthy`, `at-risk`, or
`critical`.

### Procurement Cost Prediction

```text
POST /api/v1/predict/procurement-cost
```

| Field | Type | Validation |
|---|---|---|
| `vendor_id` | String | Required; nonblank |
| `product_category` | Enum | `Precision`, `Industrial`, `Electronics`, `Raw Materials` |
| `quantity` | Integer | Required; > 0 |
| `lead_time` | Integer | Required; ≥ 0 days |
| `market_conditions` | Enum | `stable`, `volatile`, `rising`, `falling` |

Prediction fields: `estimated_procurement_cost`, `cost_range`, and
`suggested_procurement_window`. The cost range enforces `max >= min`.

### Profitability Prediction

```text
POST /api/v1/predict/profitability
```

| Field | Type | Validation |
|---|---|---|
| `product` | String | Required; nonblank |
| `vendor` | String | Required; nonblank |
| `customer` | String | Required; nonblank |
| `quantity` | Integer | Required; > 0 |
| `sales_channel` | Enum | `online`, `retail`, `wholesale`, `direct` |

Prediction fields: `expected_profit`, `profit_margin`, and
`profitability_category`. Categories are `high`, `medium`, `low`, or `negative`.

## Model configuration

Set model URIs outside the application:

```powershell
$env:WORKING_CAPITAL_MODEL_URI = "runs:/<run-id>/model"
$env:CASH_FLOW_MODEL_URI = "runs:/<run-id>/model"
$env:PROCUREMENT_COST_MODEL_URI = "runs:/<run-id>/model"
$env:PROFITABILITY_MODEL_URI = "runs:/<run-id>/model"
```

`MODEL_URIS_JSON` can configure multiple name-to-URI mappings. Each URI must be
loadable by `mlflow.pyfunc.load_model` and its prediction must match the
corresponding response schema.

## Observability and error safety

Logs are structured JSON and include UTC timestamp, severity, logger, and event
message. Request completion logs also contain method, path, HTTP status, and
duration in milliseconds. Unexpected errors and model-loading failures retain
server-side traceback information. Responses never return those details.

## Testing and deployment gate

Run the automated suite with:

```powershell
python -m pytest
```

The test suite covers valid requests, missing fields, empty bodies, invalid
types and enums, boundaries, status codes, OpenAPI metadata, response format,
contract-layer response time, model caching, and prediction pass-through.

Before deployment, run integration and load testing with real model artifacts.
The release record should include model versions, parity results, and latency
percentiles on the target infrastructure.

## Pending endpoint contracts

The Week 6 brief identifies ten intended models but supplies contracts only for
models 5–8. Models 1–4, 9, and 10 require the following before implementation:

- model display name and URL slug;
- input names, types, ranges, defaults, dates, and enum values;
- exact output structure;
- MLflow URI and expected input representation;
- representative valid request and output.

These slots remain explicit source-code TODOs so incomplete endpoints cannot be
mistaken for production-ready APIs.
