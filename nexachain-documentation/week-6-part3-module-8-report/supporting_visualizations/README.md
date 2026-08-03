# Supporting Visualization Register

This folder is a publication plan, not a claim that new figures were rendered. Every figure must be generated from the named saved evidence, reviewed for readability, and placed next to an explanatory paragraph in the final publication.

| File name | Visual | Source | Supported claim | Design notes |
|---|---|---|---|---|
| `01-data-domain-coverage.png` | horizontal bars of row counts by domain | cleaned CSV files | breadth of analytical foundation | show exact counts; note differing grains |
| `02-supplier-risk-spend.png` | 100% stacked bar by risk category | supplier ranking/summary | 77.73% spend in high/critical risk | separate supplier count and spend share |
| `03-vendor-tier-defects.png` | dot/interval plot by tier | H2 mean comparison and vendor data | Tier-1 has materially lower defect rate | add robust confidence intervals; no causal label |
| `04-demand-model-error.png` | grouped bars for MAE/RMSE/MAPE | demand evaluation summary | SARIMA wins majority metrics; results are close | separate units or use small multiples |
| `05-demand-outlier-sensitivity.png` | before/after error comparison | demand evaluation summary | final date dominates RMSE | label exclusion as sensitivity, not preferred result |
| `06-cash-forecast.png` | 13-week line with uncertainty band | cash-flow forecast CSV | persistent negative forecast and attention weeks | include zero line and actuals if available |
| `07-treasury-stress-drivers.png` | ranked association bars | treasury analysis summary | operational drivers outweigh calendar seasonality | label as association, not causality |
| `08-api-maturity.png` | segmented status bar: 4/4/2 | code router and continuity report | production readiness is partial | colors: implemented, specified, proposed |

## QA checklist

- Neutral visual title and plain-English subtitle with period, grain, and units
- Color-blind-safe palette and readable labels at GitBook width
- Exact source and transformation metadata retained
- Adjacent interpretation states takeaway, implication, and caveat
- Static data table or alt text supplied for accessibility
- No 3D effects, truncated axes, dual-axis ambiguity, or unsupported causal wording
