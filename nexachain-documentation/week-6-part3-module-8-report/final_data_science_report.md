# NexaChain Intelligence Platform — Final Data Science Report

**Evidence snapshot:** August 3, 2026  
**Analytical data coverage:** primarily January 2021–December 2024  
**Audience:** executive sponsors, supply-chain and finance leaders, product management, and technical reviewers

## 1. Executive Summary

- **The project has established a credible analytical foundation across five operational domains.** Cleaned assets cover 122,731 orders, 86,000 shipments, 56,000 inventory snapshots, 22,080 vendor-month records, and 66,000 financial records. The strongest recorded pipeline, logistics, passed 25 of 25 post-repair validation controls.
- **The evidence supports immediate decision support, with important risk concentrations.** In the latest supplier scorecard, 350 of 460 suppliers are high or critical risk and represent 77.73% of procurement spend. Tier-1 vendor defect rates are materially lower than Tier-2 and Tier-3 rates. Treasury analysis identifies stress concentration but weak calendar seasonality, so cost and transaction drivers deserve more attention than simple seasonal rules.
- **Forecasts are useful for planning but not yet autonomous commitments.** SARIMA slightly outperformed Prophet on the demand evaluation majority rule. The 13-week cash-flow model recorded MAE of $14.1M, RMSE of $18.3M, and MAPE of 36.1%, while forecasting a cumulative negative $618.1M. That signal warrants scenario planning and intervention, but the error scale requires human treasury judgment.
- **Production readiness is partial.** Four of ten target FastAPI routes are implemented and tested: working capital, cash flow, procurement cost, and profitability. Four more are specified but unregistered; demand forecast and supplier score remain proposed. Docker, CI/CD, authentication, remote model registry, production monitoring, and SHAP artifacts were not found in the repository snapshot.

The recommended course is a controlled pilot: act on supplier and treasury insights now through reviewed workflows, finish the six API contracts, implement the production control plane, and require explainability and outcome monitoring before automating high-impact decisions. A standalone summary is available in [`executive_summary.md`](executive_summary.md); detailed actions are in [`business_recommendations.md`](business_recommendations.md).

## 2. Business Problem

NexaChain manages interdependent decisions across demand, inventory, logistics, vendors, procurement, profitability, working capital, and cash. When those decisions are made from disconnected files or retrospective dashboards, teams react late to stockouts, delivery delays, supplier deterioration, adverse cost movement, and liquidity stress.

The business problem is therefore not simply to build ten prediction models. It is to create an auditable decision system that:

- brings cross-domain evidence to the point of decision;
- forecasts future exposure early enough for action;
- provides stable enterprise APIs;
- communicates uncertainty and model limitations;
- records which data and model version informed an action; and
- monitors whether the action improved service, cost, resilience, or cash.

The core risk is false confidence: a technically valid score can still be operationally harmful if its target, time horizon, threshold, or data freshness is unclear. Module 5 establishes the traceability controls intended to prevent that failure.

## 3. Project Objectives

| Objective | Business outcome | Acceptance evidence | Current assessment |
|---|---|---|---|
| Create trusted cross-domain data | consistent, auditable decisions | quality checks and curated datasets | substantially achieved; canonicalization remains |
| Generate predictive insight | earlier intervention | backtests, uncertainty, cohort performance | achieved for selected forecasts; uneven across use cases |
| Expose models as APIs | enterprise integration | registered route, schema, tests, model package | 4 of 10 target routes implemented |
| Operationalize models | repeatable release and rollback | MLflow registry, CI/CD, container, monitoring | partial/proposed |
| Explain decisions | reviewer and user trust | SHAP artifacts, model cards, limitations | not evidenced in snapshot |
| Convert evidence into action | measurable business value | playbooks, owners, controlled pilots | recommendations defined; outcome test pending |

Success should be measured through a balanced scorecard: forecast error and calibration, on-time delivery, stockout rate, procurement cost variance, supplier-risk exposure, cash forecast error, API availability/latency, override rate, and realized value from interventions.

## 4. Dataset Overview

The analytical layer spans five cleaned domains. Counts below describe repository files rather than a live production warehouse.

| Dataset | Rows | Columns | Business grain | Primary date coverage | Recorded null cells |
|---|---:|---:|---|---|---:|
| Orders | 122,731 | 36 | order | 2021-01-01 to 2024-12-31 | 278,150 |
| Logistics | 86,000 | 47 | shipment | 2021-01-01 to 2024-12-31 dispatch | 323,060 |
| Inventory | 56,000 | 29 | product/warehouse snapshot | 2021-01-01 to 2024-12-31 | 0 |
| Vendors | 22,080 | 33 | vendor/month snapshot | contract dates span 2015–2026 | 0 |
| Financials | 66,000 | 30 | finance record | 2021-01-01 to 2024-12-31 | 143,797 |

Many nulls are structurally legitimate. Examples include arrival fields for active shipments, port fields for non-ocean modes, return reasons for non-returned orders, and financial measures not applicable to every transaction type. Null counts must therefore be interpreted against conditional completeness rules, not treated as uniform defects.

Two finance files, `financials_clean.csv` and `financials_cleaned.csv`, have the same observed shape. Production lineage should nominate one canonical asset. The complete source-to-outcome mapping is in Module 5.

## 5. Data Preparation

Preparation followed a domain-aware pattern: normalize schema and values, deduplicate business keys, repair only deterministic corruption, derive reconciliation flags, retain explainable long tails, and validate output invariants.

The logistics pipeline demonstrates this approach concretely:

| Repair | Rows affected |
|---|---:|
| Duplicate shipment identifiers removed | 2,580 |
| Transport-mode values normalized | 1,671 |
| Shipment weights deterministically recovered | 1,670 |
| Delivered arrival dates recovered | 2,335 |
| Delay days recalculated | 5,951 |
| Late shipments assigned an unknown reason | 2,629 |
| Negative freight signs corrected | 826 |
| Eightfold fuel-surcharge corruption corrected | 2,580 |

The resulting 86,000-row dataset has unique shipment identifiers and passed all 25 documented checks, including date consistency, cost reconciliation, valid modes, foreign-key coverage to orders, and weather/customs logic. Plausible operational outliers were retained because global clipping would erase genuine variation across transport modes.

Remaining controls should include immutable source hashes, formal schema versions, late-arriving-data policy, automated cross-domain reconciliation, and one orchestrated clean-data release process. These are prerequisites for reproducible retraining.

## 6. Exploratory Data Analysis

Exploration focused on operational risk, supplier performance, pricing evidence, and cash behavior.

**Supplier exposure is the clearest portfolio concentration.** The December 2024 scorecard covers 460 suppliers. Its mean dynamic score is 67.66; 121 suppliers are improving and 104 are deteriorating under the documented six-month comparison rule. More importantly, high or critical risk suppliers account for 77.73% of spend. This does not imply immediate replacement of most suppliers; it shows that mitigation must prioritize spend-weighted exposure.

**Treasury stress is large but not explained by simple seasonality.** The analysis covers 210 weeks and identifies 20 stress weeks. The worst week, beginning January 23, 2023, recorded cash flow of negative $121.6M. Calendar tests do not establish useful month/season effects: ANOVA p = 0.715, Kruskal p = 0.830, and lag-52 autocorrelation is -0.069. Operational cost, SLA penalties, revenue, and logistics cost have stronger associations with stress than calendar position.

**The requested deep-discount test is unsupported by coverage.** Among 122,731 analyzable orders, none has a discount above 30%; the observed maximum is 25%. Spearman correlation between discount percentage and margin is positive at 0.447, contrary to the original negative hypothesis, but this is association rather than causality and may reflect product mix or the margin definition.

These findings motivate three decisions: prioritize supplier exposure by spend and trend, build event-based treasury scenarios, and avoid a blanket discount restriction without additional data and margin-definition validation.

## 7. Feature Engineering

Feature design must reflect the decision timestamp and entity grain. Representative feature families include:

| Domain | Feature families | Point-in-time constraint |
|---|---|---|
| Demand | unit lags, rolling averages, weekday/month, promotion, product/warehouse | only orders known before forecast origin |
| Logistics | carrier/route history, mode, distance, weight, customs, planned transit | exclude realized arrival, delay, and post-dispatch events |
| Inventory | available stock, days of supply, demand velocity, lead time, safety stock | exclude future receipts and realized stockout |
| Suppliers | lagged delivery/quality, stability, concentration, dispute and disruption history | use snapshots available as of score date |
| Finance | AR/AP/inventory, cash lags, fiscal periods, cost/revenue mix | respect ledger-close availability |
| Profitability | product/vendor/customer/channel, quantity, price and allowed commercial terms | exclude realized outcome for pre-sale prediction |

The supplier scorecard uses five documented components: 30% on-time delivery, 20% quality, 20% risk performance, 15% cost efficiency, and 15% lead time. That formula should be versioned and separated from any machine-learned risk probability.

Production feature engineering requires a shared transformation package, fitted-statistic persistence, feature dictionaries with units, categorical unknown handling, and training-serving parity tests. Percentages must use one declared scale; the proposed vendor API currently needs that decision.

## 8. Statistical Methodology

The project uses descriptive statistics, hypothesis testing, association analysis, and time-series validation.

For vendor quality, monthly records were aggregated to one record per vendor to improve independence. Mean defect rates are 4.50% for Tier-1, 11.82% for Tier-2, and 20.02% for Tier-3. One-way ANOVA reports F = 872.08, p ≈ 9.89×10⁻¹⁵⁷, and eta-squared = 0.792. Variance equality is not supported (Levene p ≈ 2.00×10⁻¹³), and Tier-2 normality is weak, so the magnitude is persuasive but should be supplemented with robust/Welch analysis before policy thresholds are finalized.

For discount and margin, non-normality led to Spearman as the primary association measure. The result is statistically precise because of the large sample, but it cannot answer the absent >30% threshold question and does not identify causal discount effects.

Forecast evaluation uses MAE, RMSE, and MAPE. Time-dependent use cases should use rolling-origin evaluation, prediction-interval coverage, and sensitivity to influential dates. Multiple-comparison control, effect sizes, confidence intervals, and prespecified hypotheses should be standard for future analytical releases.

## 9. Machine Learning Models

The repository provides direct evidence for demand and cash-flow forecasting and service contracts for four inference domains.

| Use case | Evidence/model family | Maturity |
|---|---|---|
| Demand forecast | SARIMA and Prophet tracked in MLflow | evaluated; API pending |
| Cash flow | 13-week forecast artifacts | evaluated; API contract implemented |
| Working capital | MLflow `pyfunc` service contract | API implemented; packaged model URI required |
| Procurement cost | MLflow `pyfunc` service contract | API implemented; packaged model URI required |
| Profitability | MLflow `pyfunc` service contract | API implemented; packaged model URI required |
| Delivery/vendor/stockout/route risk | continuity contracts | not registered in current code |
| Supplier score | deterministic weighted score proposed | contract and route pending |

The demand MLflow file store includes four completed runs: baseline and notebook variants for SARIMA and Prophet. Forecast CSV artifacts and MAE/RMSE/MAPE metrics are present. There is no evidence of a shared remote registry or approved production alias.

Model selection should remain use-case specific. Forecasting models need uncertainty and regime sensitivity; risk classifiers need calibration and cost-sensitive thresholds; deterministic supplier scoring needs governance of weights and scale rather than claims of learned prediction.

## 10. Model Evaluation

### Demand forecasting

| Model | MAE | RMSE | MAPE | Majority-metric winner |
|---|---:|---:|---:|---|
| SARIMA | 2,831.61 | 21,849.37 | 19.01% | Yes |
| Prophet | 2,859.00 | 21,840.65 | 20.34% | No |

The two models are close, and RMSE slightly favors Prophet. SARIMA wins two of three recorded metrics. Excluding December 31, 2024 reduces SARIMA RMSE from 21,849 to 666 and Prophet RMSE to 702, demonstrating that one influential period dominates the aggregate result. That point must be investigated rather than silently excluded.

### Cash-flow forecasting

The 13-week forecast reports MAE of $14.1M, RMSE of $18.3M, and MAPE of 36.1%. It forecasts cumulative cash flow of negative $618.1M, averaging negative $47.5M weekly, with four attention weeks. This is decision-relevant as a stress signal, but the forecast error is too large for unreviewed funding commitments.

### Required release evaluation

Future model gates should include baseline lift, interval coverage or probability calibration, worst-cohort performance, stability by time, latency/resource cost, threshold economics, and post-deployment outcome measurement. Aggregate accuracy alone is insufficient.

## 11. Explainable AI (SHAP)

SHAP should explain how each feature moved a model output relative to its baseline. Global summaries can identify dominant drivers; local explanations can support a planner reviewing a high-risk route, supplier, or stockout prediction. Dependence and interaction analysis can reveal non-linear thresholds.

No persisted SHAP plots, values, or explainability validation were found in the repository snapshot. Accordingly, this report does not claim SHAP findings. Before release, each learned model should provide:

- a representative background dataset and explainer configuration;
- global mean absolute SHAP importance with cohort comparisons;
- local explanations for approved test cases and high-impact predictions;
- stability checks across retraining runs;
- business review for implausible or proxy drivers; and
- a clear statement that attribution is not causality.

Sensitive or commercially restricted variables require a separate review. Explanations exposed through APIs should be bounded, versioned, and designed not to leak training data.

## 12. API Development

The FastAPI application uses a v1 router, endpoint-specific strict Pydantic schemas, dependency-injected cached models, validated model outputs, standardized success envelopes, and centralized sanitized errors. Automated tests cover successful contracts, missing and invalid fields, enum/range boundaries, unknown fields, model unavailability, output validation, and parity between model output and API response.

| Status | Count | Endpoints |
|---|---:|---|
| Implemented and registered | 4 | working-capital, cash-flow, procurement-cost, profitability |
| Specified but unregistered | 4 | delivery-delay, vendor-risk, stockout, route-risk |
| Proposed | 2 | demand-forecast, supplier-score |

The current service has no authentication layer. It also lacks model-version response metadata, correlation IDs, health/readiness routes, rate limiting, and explicit production SLOs. Module 6 supplies the full ten-endpoint contract, developer workflow, and Swagger capture procedure while preserving these maturity labels.

## 13. Docker Deployment

The continuity report states that endpoints are containerized on port 8000, but no Dockerfile, Compose manifest, or orchestrator definition was found in the repository snapshot. Container deployment must therefore be treated as a target-state deliverable rather than verified current capability.

The recommended runtime is a pinned Python 3.11 slim image, non-root user, read-only filesystem where feasible, immutable image digest, injected model URIs and credentials, resource limits, and startup/liveness/readiness probes. CI should generate an SBOM, scan dependencies and image layers, and sign the artifact. Deployment should progressively expose traffic and pair one API image digest with one approved model-version manifest.

The container must not embed credentials or point production at an unversioned workstation artifact. Model download and startup duration should be measured before probe thresholds and replica behavior are set.

## 14. MLOps & MLflow

MLflow is used locally for demand forecasting and is integrated into the API loader through `mlflow.pyfunc.load_model`. Four finished demand runs record parameters, metrics, and forecast artifacts. This establishes the beginning of experiment traceability.

Production operationalization still requires a remote tracking backend, controlled artifact store, registered immutable model versions, environment aliases, access control, retention rules, signature validation, and deployment linkage. The current SQLite file is empty and the active evidence is a local file store; no registered-model metadata is present.

A model release should record data fingerprint, date range, row count, schema, code SHA, dependencies, feature version, parameters, evaluation artifacts, approvers, image digest, and rollback version. Monitoring should connect service telemetry to input drift, output drift, forecast error or calibration, and realized business outcomes.

## 15. Business Insights

1. **Supplier exposure is systemic, not isolated.** High/critical-risk suppliers account for 77.73% of spend. A blanket replacement program is impractical; actions must combine spend, trend, substitutability, quality, concentration, and contractual timing.
2. **Quality differentiation across tiers is economically meaningful.** Tier-1 mean defect rate is 4.50%, versus 11.82% and 20.02% for Tiers 2 and 3. Quality-sensitive categories should reflect this evidence, subject to cost and concentration trade-offs.
3. **Liquidity needs event-based management.** Calendar seasonality is weak, while operational cost, penalties, revenue, and logistics cost are more closely associated with stress. Treasury playbooks should model these drivers directly.
4. **The cash outlook requires immediate scenario review.** The available 13-week projection is deeply negative, but with substantial error. It should trigger best/base/worst scenarios, liquidity buffers, and collection/payment interventions rather than an automatic decision.
5. **A blanket deep-discount restriction is not evidence-based here.** No observed order exceeds 30% discount, and the observed association with margin is positive. Pricing decisions require product-mix controls and verified post-discount margin definitions.
6. **The platform’s largest near-term risk is operationalization debt.** Analytical assets are ahead of security, deployment, registry, and monitoring controls. Scaling usage before closing this gap would amplify model and integration risk.

## 16. Recommendations

### First 30 days

- Establish a cross-functional model and data governance board with named owners.
- Select canonical curated datasets and publish schema/data contracts.
- Triage the negative cash forecast through scenarios and weekly treasury review.
- Create a spend-weighted supplier mitigation queue; begin with deteriorating, high-exposure, replaceable suppliers.
- Approve precise contracts for all six missing endpoints, including percentage scales and decision horizons.

### Days 31–60

- Implement and test the six missing routes; add authentication, readiness, correlation IDs, model version, and rate limiting.
- Package shared training/inference transformations and add temporal backtests and cohort gates.
- Deploy a remote MLflow backend and registry workflow.
- Add SHAP artifacts and model cards for every learned production candidate.
- Build a secure container and CI pipeline with scans, signatures, and OpenAPI compatibility checks.

### Days 61–90

- Run shadow or human-in-the-loop pilots for supplier, inventory, and treasury decisions.
- Define SLOs, drift and outcome dashboards, alerts, and rollback thresholds.
- Measure intervention value against predeclared baselines and guardrails.
- Promote only models that pass technical, business, security, and operational gates.

Detailed owners, measures, and decision gates are provided in [`business_recommendations.md`](business_recommendations.md).

## 17. Future Enhancements

- Build a point-in-time feature platform with reusable online/offline definitions.
- Add probabilistic and hierarchical demand forecasting across product and warehouse levels.
- Introduce graph-based supplier and route concentration analytics.
- Optimize inventory and sourcing actions using forecast distributions and explicit service/cost constraints.
- Add causal pricing experimentation rather than relying on observational correlation.
- Integrate external market, weather, port, commodity, and macroeconomic signals under governed contracts.
- Provide scenario simulation and what-if interfaces for planners.
- Add champion/challenger evaluation, automated retraining triggers, and drift-aware rollback.
- Extend model monitoring to fairness, stability, explanation drift, and human override analysis.

Enhancements should be sequenced by decision value and governance readiness. New model complexity should not outrun data quality, observability, or the organization’s ability to act.

## 18. Conclusion

NexaChain has moved beyond exploratory analysis: it has validated domain datasets, material supplier and treasury findings, evaluated forecasting artifacts, local MLflow tracking, and a tested four-endpoint inference foundation. The project’s evidence is strong enough to support controlled business action and a productionization program.

It is not yet a fully production-ready ten-model platform. Six routes, authentication, container evidence, CI/CD, remote registry governance, monitoring, and SHAP evidence remain incomplete. The correct next step is neither to discard the work nor to overstate it. NexaChain should convert its strongest insights into reviewed pilots while closing the release-control gaps described in Modules 5–7. That approach preserves trust, creates measurable value, and builds a defensible path from analytical prototype to enterprise intelligence platform.
