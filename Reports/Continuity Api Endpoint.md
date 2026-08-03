# NexaChain Intelligence Platform - API Endpoints Report

This document outlines the 8 production-ready machine learning prediction endpoints currently developed and integrated into the FastAPI gateway. These endpoints are containerized and accessible via Docker on port `8000`.

## Base URL
`http://localhost:8000/api/v1/predict/`

## Standard Response Format
All endpoints return a standardized JSON envelope:
```json
{
  "status": "success",
  "model": "Model Name",
  "prediction": { ... },
  "timestamp": "2026-07-30T15:30:00Z"
}
```

---

## 1. Delivery Delay Prediction (Amit's Task)
**Endpoint:** `POST /delivery-delay`
**Description:** Predicts the probability of a delivery delay and expected delay in days.

### Request Payload (JSON)
```json
{
  "carrier_id": "string",
  "route_id": "string",
  "carrier_type": "string",
  "shipment_weight": 0.0,
  "origin": "string",
  "destination": "string",
  "customs_clearance_days": 0.0
}
```

### Response Payload (JSON - inside `prediction`)
```json
{
  "delay_probability": 0.15,
  "expected_delay_days": 1.5,
  "risk_category": "Low"
}
```

---

## 2. Vendor Risk Prediction (Amit's Task)
**Endpoint:** `POST /vendor-risk`
**Description:** Predicts the vendor risk score, classification, and recommendations.

### Request Payload
```json
{
  "vendor_id": "string",
  "on_time_delivery_rate": 0.0,
  "quality_acceptance_rate": 0.0,
  "financial_stability_score": 0.0,
  "concentration_risk_percentage": 0.0
}
```

### Response Payload
```json
{
  "vendor_risk_score": 75.5,
  "risk_classification": "Moderate",
  "recommendation": "Monitor Quality Output"
}
```

---

## 3. Inventory Stockout Prediction (Amit's Task)
**Endpoint:** `POST /stockout`
**Description:** Predicts the probability of a stockout and recommended reorder quantities.

### Request Payload
```json
{
  "product_id": "string",
  "warehouse_id": "string",
  "stock_on_hand": 0,
  "days_of_supply": 0.0,
  "lead_time": 0.0,
  "average_demand": 0.0
}
```

### Response Payload
```json
{
  "stockout_probability": 0.82,
  "recommended_reorder_quantity": 500,
  "risk_level": "High"
}
```

---

## 4. Route Risk Prediction (Amit's Task)
**Endpoint:** `POST /route-risk`
**Description:** Predicts the risk score and expected delays for specific shipping routes.

### Request Payload
```json
{
  "origin": "string",
  "destination": "string",
  "carrier_type": "string",
  "shipment_weight": 0.0,
  "departure_date": "2026-08-01"
}
```

### Response Payload
```json
{
  "route_risk_score": 25.0,
  "expected_delay": 0.5,
  "alternative_route_recommendation": "RTE-00150"
}
```

---

## 5. Working Capital Forecast (Samiksha's Task)
**Endpoint:** `POST /working-capital`
**Description:** Forecasts working capital and liquidity trends.

### Request Payload
```json
{
  "period_start": "2026-08-01",
  "period_end": "2026-08-31",
  "accounts_receivable_balance": 0.0,
  "accounts_payable_balance": 0.0,
  "inventory_value": 0.0
}
```

### Response Payload
```json
{
  "forecasted_working_capital": 150000.0,
  "liquidity_trend": "Stable",
  "confidence_score": 0.92
}
```

---

## 6. Cash Flow Forecast (Samiksha's Task)
**Endpoint:** `POST /cash-flow`
**Description:** Forecasts weekly cash flow and returns financial health signals.

### Request Payload
```json
{
  "forecast_weeks": 4,
  "current_cash_position": 0.0,
  "outstanding_payables": 0.0,
  "expected_receivables": 0.0
}
```

### Response Payload
```json
{
  "cash_flow_forecast": 50000.0,
  "weekly_trend": "Positive",
  "financial_health_indicator": "Healthy"
}
```

---

## 7. Procurement Cost Prediction (Samiksha's Task)
**Endpoint:** `POST /procurement-cost`
**Description:** Estimates procurement costs based on market conditions.

### Request Payload
```json
{
  "vendor_id": "string",
  "product_category": "string",
  "quantity": 0,
  "lead_time": 0.0,
  "market_conditions": "string"
}
```

### Response Payload
```json
{
  "estimated_procurement_cost": 12000.0,
  "cost_range": "11500 - 12500",
  "suggested_procurement_window": "Week 3"
}
```

---

## 8. Profitability Prediction (Samiksha's Task)
**Endpoint:** `POST /profitability`
**Description:** Estimates expected profit and margins for specific product sales.

### Request Payload
```json
{
  "product": "string",
  "vendor": "string",
  "customer": "string",
  "quantity": 0,
  "sales_channel": "string"
}
```

### Response Payload
```json
{
  "expected_profit": 4500.0,
  "profit_margin": 0.15,
  "profitability_category": "High"
}
```

---
*Note: Demand Forecast and Supplier Performance APIs are pending implementation.*