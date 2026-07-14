# Forecast Comparison Report

## Business objective
Develop baseline demand forecasting models that can support procurement planning, replenishment timing, and stock-risk reduction.

## Dataset used
- Requested source in task brief: `orders_cleaned.csv`
- Available project source used: `data/cleaned/orders_clean.csv`
- Time coverage: 2021-01-01 to 2024-12-31
- Total order rows: 122,731
- Daily observations after aggregation: 1,461

## Workflow followed
1. Aggregate order demand to daily level using `order_quantity`.
2. Reindex to a complete daily calendar and fill missing demand dates with zero.
3. Reserve the final 90 days for holdout testing.
4. Train one SARIMA baseline and one Prophet baseline independently.
5. Evaluate both models with MAE, RMSE, and MAPE.
6. Log the baselines to local MLflow tracking in `Models/mlruns`.

## Data quality and preparation notes
- Duplicate raw `order_date` values are expected because multiple orders occur per day; aggregation removed timestamp duplication risk at the forecasting grain.
- Missing daily dates after reindexing: 0
- Extreme spike detected on 2024-12-31: 210,469 units
- To keep future forecasts stable, the 30-day forward forecast was refit on a version of the series capped at the 99.5th percentile. Holdout evaluation remained on the raw demand series.

## Train/test split
- Training window: 2021-01-01 to 2024-10-02
- Testing window: 2024-10-03 to 2024-12-31

## Seasonality findings
- Highest average demand day: Tuesday (4,244.9 units)
- Lowest average demand day: Monday (3,194.0 units)
- Highest average demand month: December (4,927.8 units)
- Lowest average demand month: July (3,184.5 units)

## Model evaluation summary
| model | mae | rmse | mape | mae_excluding_2024_12_31 | rmse_excluding_2024_12_31 | mape_excluding_2024_12_31 | winner_majority_metrics |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SARIMA | 2831.612 | 21849.373 | 19.012 | 535.496 | 666.415 | 18.120 | 1.000 |
| Prophet | 2858.998 | 21840.646 | 20.336 | 564.237 | 702.087 | 19.459 | 0.000 |

## Recommendation
SARIMA is recommended as the baseline forecasting model for follow-on optimization.

Why SARIMA was selected:
- Prophet achieved a slightly lower RMSE on the raw holdout because squared error is dominated by the 2024-12-31 spike.
- SARIMA performed better on MAE and MAPE, which are more stable for day-to-day operational planning.
- In the sensitivity check that excludes 2024-12-31, SARIMA outperformed Prophet across all three metrics.

## Product-level interpretation
- SKU-level forecasting is not yet reliable from this dataset because product IDs are too sparse across days for a daily time-series baseline.
- Category-level volatility is highest in this order: Logistics, Precision, Raw Materials, Industrial, Electronics.
- Procurement teams should begin baseline planning at the aggregate or category level, then revisit product-level models once longer SKU histories or product-family rollups are available.

## Procurement actions
- Use the SARIMA baseline for aggregate demand planning and safety-stock review.
- Add a business review for the 2024-12-31 spike before treating it as a repeatable pattern.
- Prioritize replenishment readiness around Tuesdays and the November-December period, where average demand is strongest.
- Track category-level exceptions in Logistics, Precision, and Raw Materials first because they show the largest volatility signals.

## Generated artifacts
- `historical_demand.png`
- `sarima_forecast.png`
- `prophet_forecast.png`
- `forecast_comparison.png`
- `stl_components.png`
- `prophet_components.png`
- `model_evaluation_summary.csv`
- `sarima_test_forecast.csv`
- `prophet_test_forecast.csv`
- `sarima_future_30_day_forecast.csv`
- `prophet_future_30_day_forecast.csv`
