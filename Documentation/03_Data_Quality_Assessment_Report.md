# Data Quality Assessment Report

## Executive Summary

The datasets are rich and usable, but several material quality issues should be addressed before advanced reporting or modeling. The largest risks are duplicated datasets, incomplete key relationships, inconsistent status formatting, and business rule violations in orders, inventory, and financial data.

## Missing Values

### `orders.csv`

- `return_reason`: 97.02%
- `actual_delivery_date`: 39.85%
- `delivery_delay_days`: 39.85%
- `warehouse_id`: 25.09%
- `shipment_id`: 24.83%
- `profit_margin_pct`: 5.00%

### `inventory.csv`

- `vendor_lead_time_days`: 5.00%
- `reorder_point`: 4.00%

### `vendors.csv`

- `financial_stability_score`: 12.00%
- `quality_acceptance_rate`: 8.00%
- `vris_score`: 7.00%

### `financials.csv`

- `shipment_id`: 88.12%
- `vendor_id`: 79.84%
- `order_id`: 49.82%
- `financial_risk_score`: 7.97%
- `working_capital_ratio`: 6.01%

## Duplicate Records

- `orders.csv`: 0 exact duplicate rows
- `inventory.csv`: 0 exact duplicate rows
- `vendors.csv`: 0 exact duplicate rows
- `financials.csv`: 3,300 exact duplicate rows
- `logistics.csv`: exact duplicate of `orders.csv`

## Data Type and Standardization Issues

- Several date fields were stored as text and require explicit date parsing.
- `order_status` contains both title case and uppercase versions of the same business states.
  - Examples: `Delivered` and `DELIVERED`, `Cancelled` and `CANCELLED`
- This inconsistency can fragment reporting unless standardized.

## Business Rule Violations

### Orders

- Negative order values: 2,513
- Actual delivery date earlier than order date: 4,503
- Profit margin missing even though order value is positive: 6,149
- Return reason populated for non-returned and non-cancelled orders: 121

### Inventory

- `available_stock` mismatch against `stock_on_hand - units_reserved`: 3,360
- Negative `stock_on_hand`: 3,360
- `stockout_flag` mismatch versus actual available stock condition: 18,864
- `total_inventory_value_usd` mismatch against `stock_on_hand * unit_cost_usd`: 3,360
- `last_issue_date` earlier than `last_receipt_date`: 40,549
  - This may represent valid business history in some cases, but it should be confirmed with the business owner.

### Financials

- Gross profit mismatch against `revenue - procurement - logistics - sla penalty`: 24,353

## Relationship Integrity Issues

- Only about 38% of order rows reference vendor IDs found in `vendors.csv`.
- Only about 39% of inventory rows reference vendor IDs found in `vendors.csv`.
- All non-null financial order IDs match orders, which is positive.
- No non-null financial shipment IDs matched shipment IDs in orders, which is a major integration concern.
- One unmatched product ID appears in orders: `PRD-ORPHAN`

## Outliers

IQR-based outlier volumes indicate heavy-tailed business behavior and possible anomalies:

- `orders.order_value_usd`: 17,052 outliers
- `orders.gross_margin_usd`: 16,657 outliers
- `inventory.stock_on_hand`: 6,898 outliers
- `inventory.total_inventory_value_usd`: 7,271 outliers
- `financials.revenue_usd`: 13,151 outliers
- `financials.financial_risk_score`: 3,425 outliers

These should not be deleted automatically because some may reflect real high-value or high-risk cases.

## Recommended Next Actions

1. Standardize status and categorical values.
2. Remove exact duplicate rows from `financials.csv`.
3. Confirm whether `logistics.csv` should exist separately from `orders.csv`.
4. Reconcile vendor master coverage and shipment ID relationships.
5. Review negative order values and gross profit calculation logic with business stakeholders.
6. Clarify the intended logic for `stockout_flag` and inventory history dates.
