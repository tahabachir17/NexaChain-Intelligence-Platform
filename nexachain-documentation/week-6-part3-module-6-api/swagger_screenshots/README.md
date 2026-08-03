# Swagger Screenshot Runbook

This folder intentionally contains descriptions rather than fabricated screenshots. Capture images only from a running, version-matched service.

## Required captures

1. `01-swagger-overview.png` — `/docs` page showing service title, version, and all registered tags.
2. `02-working-capital.png` — expanded request schema, example, and 200/400/503 responses.
3. `03-cash-flow.png` — forecast horizon constraints and nested weekly response.
4. `04-procurement-cost.png` — enum fields and cost-range response.
5. `05-profitability.png` — channel enum and profitability categories.
6. `06-openapi-json.png` — `/openapi.json` metadata and version.
7. `07-authentication.png` — authorization dialog after security is implemented.

## Procedure

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`, use a 1440×900 viewport, remove secrets from examples, and record the commit SHA and API version in the pull request. The four implemented endpoints should be captured now; the other six must wait until their routes are registered.
