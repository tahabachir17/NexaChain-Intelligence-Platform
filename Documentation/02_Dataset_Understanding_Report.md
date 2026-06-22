# Dataset Understanding Report

## Overview

Five CSV datasets were provided in the `data/` folder. Together they describe operational, inventory, supplier, logistics, and financial activity from 2021 to 2025.

## Dataset Summary

### `orders.csv`

- Shape: 125,660 rows x 28 columns
- Date range: 2021-01-01 to 2025-06-15
- Business role: transactional order dataset
- Main entities: customers, products, vendors, shipments, warehouses
- Key metrics: `order_value_usd`, `gross_margin_usd`, `profit_margin_pct`, `delivery_delay_days`, `discount_pct`
- Use cases:
  - order performance analysis
  - delay and fulfillment analysis
  - profitability by product, region, customer segment, or vendor

### `logistics.csv`

- Shape: 125,660 rows x 28 columns
- Business role: expected logistics/fulfillment dataset
- Important finding: this file is an exact duplicate of `orders.csv`
- Use case implication: treat as duplicate until clarified by the project owner

### `inventory.csv`

- Shape: 56,000 rows x 26 columns
- Date range: 2021-01-01 to 2024-12-31
- Business role: inventory snapshots by product and warehouse
- Main entities: products, warehouses, vendors
- Key metrics: `stock_on_hand`, `available_stock`, `reorder_point`, `days_of_supply`, `total_inventory_value_usd`, `stockout_flag`
- Use cases:
  - stock health monitoring
  - stockout detection
  - reorder planning
  - warehouse-level inventory optimization

### `vendors.csv`

- Shape: 22,080 rows x 30 columns
- Date range: 2021-01-01 to 2024-12-01
- Business role: monthly supplier performance and risk snapshots
- Main entities: vendors, tiers, regions, categories
- Key metrics: `on_time_delivery_rate`, `quality_acceptance_rate`, `lead_time_avg_days`, `procurement_spend_usd`, `vris_score`, `risk_category`
- Use cases:
  - vendor risk ranking
  - supplier scorecards
  - sourcing strategy and preferred vendor analysis

### `financials.csv`

- Shape: 69,300 rows x 28 columns
- Date range: 2021-01-01 to 2024-12-31
- Business role: financial transaction and risk tracking
- Main entities: orders, vendors, shipments, transaction types
- Key metrics: `revenue_usd`, `procurement_cost_usd`, `logistics_cost_usd`, `gross_profit_usd`, `ebitda_usd`, `working_capital_ratio`, `cash_flow_usd`, `financial_risk_score`
- Use cases:
  - profitability analysis
  - cost structure analysis
  - cash-flow monitoring
  - financial risk monitoring

## Dataset Relationships

- `orders.order_id` links strongly to `financials.order_id`
  - Match rate for non-null financial order IDs: 100%
- `vendor_id` appears across `orders`, `inventory`, `vendors`, and `financials`
  - Coverage issue: `vendors.csv` contains 460 unique vendors, while `orders.csv` and `inventory.csv` use 1,200 vendor IDs
- `product_id` links `orders` and `inventory`
  - Most product IDs match
  - One unmatched product ID was found: `PRD-ORPHAN`
- `shipment_id` is present in `orders` and `financials`
  - No observed match between non-null shipment IDs, suggesting different ID systems or a data issue

## Business Context Interpretation

The datasets support an end-to-end view of the business:

- demand and customer activity through orders
- supply status through inventory
- vendor reliability and risk through vendor scorecards
- cost and margin performance through financials

This creates a strong foundation for descriptive analytics, operational diagnostics, and predictive modeling.
