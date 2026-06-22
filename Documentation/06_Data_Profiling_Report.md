# Data Profiling Report

## Dataset Inventory

| Dataset | Rows | Columns | Date Range |
|---|---:|---:|---|
| `orders.csv` | 125,660 | 28 | 2021-01-01 to 2025-06-15 |
| `logistics.csv` | 125,660 | 28 | same as `orders.csv` |
| `inventory.csv` | 56,000 | 26 | 2021-01-01 to 2024-12-31 |
| `vendors.csv` | 22,080 | 30 | 2021-01-01 to 2024-12-01 |
| `financials.csv` | 69,300 | 28 | 2021-01-01 to 2024-12-31 |

## Key Cardinalities

- `orders.order_id`: 122,000 unique values
- `inventory.product_id`: 3,000 unique values
- `inventory.vendor_id`: 1,200 unique values
- `vendors.vendor_id`: 460 unique values
- `financials.order_id`: 27,704 non-null unique values
- `financials.vendor_id`: 1,200 non-null unique values
- `financials.shipment_id`: 7,481 non-null unique values

## Orders Profile

- Average order quantity: 40.74
- Median order quantity: 20
- Average order value: 9,483.37 USD
- Minimum order value: -1,228,295.66 USD
- Maximum order value: 3,923,386.15 USD
- Product categories are evenly distributed across five groups.
- Regions are also broadly balanced.

### Order Status Distribution

- Delivered: 73,306
- Shipped: 18,324
- Processing: 8,550
- Cancelled: 8,368
- Confirmed: 6,155
- Returned: 3,626
- Pending: 3,561
- Additional uppercase duplicates of the same statuses are also present

## Inventory Profile

- Average stock on hand: 406.10 units
- Median stock on hand: 132 units
- Minimum stock on hand: -35,150 units
- Maximum stock on hand: 66,101 units
- Average days of supply is positive, but the spread is wide.
- Product categories are fairly evenly distributed.
- Warehouses represented: 14

## Vendor Profile

- Monthly vendor snapshots: 48 months per vendor group in the full period
- Risk categories:
  - Medium: 17,356
  - Low: 4,659
  - High: 65
- Average on-time delivery rate: 79.49%
- Average lead time: 33.47 days
- Average procurement spend: highly variable, with clear long-tail behavior

## Financial Profile

- Transaction types:
  - Revenue: 20,828
  - Procurement: 13,972
  - COGS: 13,856
  - Logistics Cost: 8,232
  - Operational Expense: 6,884
  - SLA Penalty: 3,497
  - Interest Expense: 2,031
- Average revenue per financial row: 20,144.74 USD
- Average procurement cost per financial row: 7,167.21 USD
- Average logistics cost per financial row: 456.96 USD

## Profiling Conclusions

- The data volume is sufficient for dashboarding, exploratory analysis, and ML use cases.
- Vendor master coverage is incomplete relative to transactional datasets.
- Financial and inventory anomalies need review before model training.
- `orders.csv` is the central business dataset and is the best starting point for integrated analysis.
