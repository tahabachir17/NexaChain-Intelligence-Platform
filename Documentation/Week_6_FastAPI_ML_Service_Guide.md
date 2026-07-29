# Week 6 — FastAPI ML Service Guide

## Status

The project now has one centralized, versioned FastAPI service for MLflow
inference. All four contracts supplied in the Week 6 brief are implemented and
tested. The other six model slots (1–4, 9, and 10) remain blocked on their model
names and request/response specifications; they are explicitly marked in
`app/api/v1/router.py` rather than represented by invented APIs.

Implemented routes:

| Model | Route |
|---|---|
| Working Capital Forecast | `POST /api/v1/predict/working-capital` |
| Cash Flow Forecast | `POST /api/v1/predict/cash-flow` |
| Procurement Cost Prediction | `POST /api/v1/predict/procurement-cost` |
| Profitability Prediction | `POST /api/v1/predict/profitability` |

Swagger UI is available at `/docs`, with endpoint-specific request models,
response models, enum choices, tags, summaries, and error responses.

## Architecture

```text
app/
|-- main.py                         application, lifespan, request logging
|-- api/v1/router.py                centralized v1 router and pending-model TODOs
|-- api/v1/endpoints/               one route module per implemented model
|-- core/config.py                  environment-based settings and model URIs
|-- core/exceptions.py              standardized global error handlers
|-- core/logging.py                 structured JSON logging
|-- models/loader.py                startup MLflow loader and in-memory cache
|-- schemas/                        shared and endpoint-specific Pydantic schemas
`-- tests/                          endpoint and infrastructure tests
```

The application lifespan creates one `ModelManager`, loads every configured URI
with `mlflow.pyfunc.load_model`, and stores each loaded model in memory. Endpoint
dependencies retrieve cached instances; models are never loaded per request.
Loading failures are logged with server-side exception details and requests to
an unavailable model receive a sanitized HTTP 503 response.

## Configuration

No model location is hardcoded. Set one or more variables before startup:

```powershell
$env:WORKING_CAPITAL_MODEL_URI = "runs:/<run-id>/model"
$env:CASH_FLOW_MODEL_URI = "runs:/<run-id>/model"
$env:PROCUREMENT_COST_MODEL_URI = "runs:/<run-id>/model"
$env:PROFITABILITY_MODEL_URI = "runs:/<run-id>/model"
uvicorn app.main:app --reload
```

`MODEL_URIS_JSON` can supply a JSON object of additional or overriding model
names and URIs. `.env.example` lists all supported settings.

## API behavior

Successful predictions use this envelope:

```json
{
  "status": "success",
  "model": "Cash Flow Forecast",
  "prediction": {},
  "timestamp": "2026-07-30T15:30:00Z"
}
```

All handled client and server errors use:

```json
{
  "status": "error",
  "message": "forecast_weeks is required.",
  "error_code": 400
}
```

Request validation failures return HTTP 400, including missing fields, invalid
ISO dates, reversed working-capital periods, negative amounts, invalid ranges,
unknown fields, and enum violations. Unconfigured models return 503. Invalid
model output and unexpected failures return sanitized 500 responses. Internal
exceptions, stack traces, file paths, and model loader details are only logged.
Starlette-generated errors such as unknown routes use the same standard format.

Structured request logs include UTC timestamp, HTTP method, path, status, and
duration. Errors include server-side diagnostic context and stack traces where
an exception is available.

## Validation notes

- Working Capital enforces ISO dates, `period_end >= period_start`, nonnegative
  balances, a liquidity-trend enum, and confidence between 0 and 1.
- Cash Flow enforces 1–52 weeks, nonnegative balances, and the health enum
  `healthy`, `at-risk`, or `critical`.
- Procurement Cost enforces nonblank vendor IDs, positive quantity, nonnegative
  lead time, the four specified market-condition values, and product categories
  found in the project data: `Precision`, `Industrial`, `Electronics`, and
  `Raw Materials`.
- Profitability enforces nonblank identifiers, positive quantity, the four sales
  channels, and the profitability-category output enum.

## Verification

Run from the project root:

```powershell
python -m pytest
python -m compileall -q app
```

Final verification result: **69 passed**. The only warning is an upstream
FastAPI `TestClient` deprecation notice and does not affect application behavior.
OpenAPI generation was also checked directly and contains all four specified
prediction paths and 23 component schemas.

Tests use injected fake model objects so API contracts are deterministic and do
not require production artifacts. They cover each endpoint independently with
valid input, invalid input, every missing field, empty payloads, invalid data
types, boundary/edge cases, response-time checks, and model-output parity.
Shared tests cover OpenAPI metadata, standardized 404 handling, and load-once
caching.

## Required input for the remaining six models

Before models 1–4, 9, and 10 can be implemented, provide for each:

- display name and endpoint slug;
- required and optional request fields;
- types, numeric ranges, date rules, and allowed enum values;
- exact prediction output fields and shapes;
- MLflow URI or artifact location;
- one representative valid request and model output.

Once supplied, each can follow the existing schema → dependency → route → test
pattern without restructuring the application. Docker files are intentionally
excluded because they belong to Part 2.
