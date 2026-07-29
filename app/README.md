# ML Model Inference API

This directory contains the centralized Week 6 FastAPI application. Four model
contracts supplied in the task are implemented:

- `POST /api/v1/predict/working-capital`
- `POST /api/v1/predict/cash-flow`
- `POST /api/v1/predict/procurement-cost`
- `POST /api/v1/predict/profitability`

The six unspecified model slots (1-4, 9, and 10) remain explicit TODOs in
`api/v1/router.py`; their business inputs and outputs must be supplied before
implementation.

## Local setup

Use Python 3.11 or newer in a virtual environment:

```powershell
pip install -r requirements.txt
$env:CASH_FLOW_MODEL_URI = "runs:/<run-id>/model"
uvicorn app.main:app --reload
```

Each endpoint has a dedicated environment variable in `.env.example`.
`MODEL_URIS_JSON` can configure several models at once. Any URI supported by
`mlflow.pyfunc.load_model` is accepted, including local artifact paths,
`runs:/...`, and `models:/...`. Configured models load once during application
startup and stay cached for reuse.

Swagger UI is at `http://127.0.0.1:8000/docs`. Run all tests with:

```powershell
python -m pytest
```

The current suite contains 69 passing tests. The endpoint testing report and
GitBook-ready API design are under `Documentation/`.

## Model output contracts

Each MLflow pyfunc model must return the prediction object documented by its
Pydantic response schema under `app/schemas/`. The API validates model output
before responding. Invalid outputs produce a sanitized HTTP 500 response and
are logged server-side.

Requests use strict, endpoint-specific schemas. Unknown fields, missing fields,
invalid enums, invalid ISO dates, and out-of-range values return the standard
HTTP 400 error shape. Unconfigured or failed models return a sanitized HTTP 503.
