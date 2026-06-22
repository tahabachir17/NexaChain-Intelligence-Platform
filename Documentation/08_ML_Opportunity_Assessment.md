# ML Opportunity Assessment

## Overall Assessment

The datasets support several realistic machine learning use cases, especially around classification, regression, anomaly detection, and risk scoring. Before production modeling, data quality remediation and relationship cleanup should be prioritized.

## Potential Target Variables

### Operational Targets

- `delivery_delay_days`
- delayed vs on-time delivery class
- `stockout_flag`
- inventory shortage risk class

### Vendor Risk Targets

- `risk_category`
- high-risk vendor flag
- future disruption likelihood

### Financial Targets

- `gross_profit_usd`
- `financial_risk_score`
- `risk_flag`
- cash-flow stress class

## Prediction Opportunities

1. Delivery delay prediction
   - Type: regression or binary classification
   - Candidate features: vendor, region, product category, order quantity, warehouse, fulfillment channel, order status history

2. Stockout prediction
   - Type: binary classification
   - Candidate features: stock on hand, reorder point, vendor lead time, product category, warehouse, days of supply

3. Vendor risk prediction
   - Type: multiclass classification
   - Candidate features: delivery rate, defect rate, lead time variance, procurement spend, disruption count, dispute flag, financial stability

4. Profitability prediction
   - Type: regression
   - Candidate features: order size, discounts, cost of goods, vendor, product category, region, fulfillment channel

5. Financial risk flag prediction
   - Type: binary classification
   - Candidate features: working capital, cash flow, DSO, DPO, inventory value, order-linked operational performance

## Feature Engineering Opportunities

- date-derived fields such as month, quarter, weekday, seasonality indicators
- standardized order status groups
- vendor performance aggregates over rolling windows
- warehouse-product stock pressure ratios
- lead-time variance bands
- margin percentage recalculations
- lagged financial indicators
- category and region encodings

## Model Candidates

- Logistic Regression
- Random Forest
- XGBoost or LightGBM
- Gradient Boosting Regressor
- CatBoost for mixed tabular data
- Isolation Forest for anomaly detection

## Risks and Constraints

- duplicate and inconsistent records may bias targets
- incomplete vendor master coverage reduces relationship quality
- shipment linkage issues may block some end-to-end use cases
- negative order values and financial inconsistencies require target validation

## Recommended ML Starting Point

The best first ML use case is likely delivery delay or stockout prediction because:

- the target is business-relevant
- the feature space is rich
- the operational value is clear
- the models can support both dashboards and action planning
