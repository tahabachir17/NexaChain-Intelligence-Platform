# NexaChain Prediction API — Quick Reference

**Base URL:** `http://localhost:8000/api/v1`  
**Content type:** `application/json`  
**Authentication in current code:** none  
**Production recommendation:** OAuth 2.0 client credentials or gateway-managed API keys over TLS.

| Endpoint | Method | Status in repository | Primary response |
|---|---|---|---|
| `/predict/demand-forecast` | POST | Proposed; pending contract approval | demand forecast by horizon |
| `/predict/delivery-delay` | POST | Specified; route not registered | delay probability and days |
| `/predict/vendor-risk` | POST | Specified; route not registered | vendor risk score and action |
| `/predict/stockout` | POST | Specified; route not registered | stockout probability and reorder quantity |
| `/predict/working-capital` | POST | Implemented and tested | working capital, trend, confidence |
| `/predict/cash-flow` | POST | Implemented and tested | weekly forecast, trend, health |
| `/predict/procurement-cost` | POST | Implemented and tested | estimate, range, buying window |
| `/predict/profitability` | POST | Implemented and tested | profit, margin, category |
| `/predict/route-risk` | POST | Specified; route not registered | route risk and alternative |
| `/predict/supplier-score` | POST | Proposed; pending contract approval | composite score and component scores |

## Standard envelopes

```json
{"status":"success","model":"Model Name","prediction":{},"timestamp":"2026-08-03T10:15:30Z"}
```

```json
{"status":"error","message":"field is required.","error_code":400}
```

Implemented routes return `400` for request validation, `500` for invalid model output or unexpected failures, and `503` when a model is unavailable. Unregistered target routes return `404` in the current application.
