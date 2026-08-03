# NexaChain Business Recommendations

## Priority 1 — Protect liquidity with scenario-based treasury action

**Evidence.** The 13-week forecast totals negative $618.1M, with average weekly forecast of negative $47.5M. Forecast MAE is $14.1M and MAPE is 36.1%; four weeks are flagged for attention.

**Action.** Create best/base/worst cash scenarios and a weekly cash council. Model collections, payment timing, procurement commitments, logistics costs, SLA penalties, and discretionary operational costs. Use thresholds to trigger executive review, not automatic payment changes.

**Measures.** Weekly forecast MAE and interval coverage; minimum projected cash buffer; overdue receivables; payable aging; realized benefit from interventions.

**Owner and gate.** CFO/Treasurer accountable; data science validates forecast; controller reconciles ledger. No automated action until rolling backtests and scenario audit pass.

## Priority 2 — Reduce supplier risk where spend and deterioration intersect

**Evidence.** High/critical risk accounts for 77.73% of spend. The scorecard identifies 104 deteriorating suppliers, five replacement candidates covering $4.34M, and three strategic-partner candidates covering $3.49M.

**Action.** Segment suppliers into mitigate, improve, replace, partner, and monitor. Rank by spend exposure, score trend, quality, lead time, concentration, substitutability, and contract renewal timing. Apply corrective action before replacement where switching risk is high.

**Measures.** High/critical spend share; defect rate; on-time delivery; concentration; corrective-action closure; avoided disruption; sourcing transition cost.

**Owner and gate.** Chief Procurement Officer accountable. Legal, operations, and finance approve material reallocations. Supplier score weights remain versioned and reviewable.

## Priority 3 — Use vendor-tier quality evidence selectively

**Evidence.** Mean defect rates are 4.50% for Tier-1, 11.82% for Tier-2, and 20.02% for Tier-3, with a large recorded effect size. Unequal variances require robust confirmation.

**Action.** Favor Tier-1 suppliers for quality- or warranty-sensitive categories while comparing cost, capacity, concentration, and lead time. Launch targeted improvement plans for high-defect Tier-2/3 suppliers.

**Measures.** Defects per received unit; warranty/return cost; cost premium; service level; concentration after reallocation.

**Owner and gate.** Procurement quality owner. Run Welch/robust sensitivity and category-level analysis before changing global policy.

## Priority 4 — Avoid unsupported blanket discount restrictions

**Evidence.** No analyzed order has discount above 30%; maximum is 25%. Discount and margin have positive Spearman correlation of 0.447, but mix and metric-definition confounding remain.

**Action.** Validate that margin is calculated after all discounts and rebates. Analyze within product, customer, channel, and time cohorts. Use controlled pricing tests for causal evidence.

**Measures.** Incremental margin, conversion, units, customer retention, and guardrail profitability by cohort.

**Owner and gate.** Commercial/pricing lead. Do not extrapolate beyond observed discount support.

## Priority 5 — Complete the six missing API capabilities safely

**Evidence.** Four of ten target routes are registered and tested. Four continuity contracts are not registered, and two contracts remain proposed.

**Action.** Approve each target, horizon, input scale, response semantics, decision threshold, and owner. Implement strict schemas, loaders, routes, contract tests, OpenAPI examples, and integration tests. Add OAuth/API gateway security, correlation IDs, model versions, health checks, rate limits, and SLOs.

**Measures.** Contract coverage; test pass rate; p95 latency; error rate; availability; model freshness; consumer adoption.

**Owner and gate.** Platform engineering accountable; product and model owner approve contract. No production label without route registration, packaged model, security, load testing, and rollback.

## Priority 6 — Establish a governed MLOps release system

**Evidence.** Local MLflow demand runs exist, but no registered models, remote backend, CI/CD configuration, or Docker artifact is evidenced.

**Action.** Implement remote tracking/artifacts, immutable model versions, environment aliases, signed container builds, dependency and image scans, staging smoke/load tests, progressive rollout, and paired model/image rollback.

**Measures.** Reproducibility rate; time to promote/rollback; failed deployment rate; untracked production versions; vulnerability remediation time.

**Owner and gate.** Head of Engineering and Model Risk jointly accountable.

## Priority 7 — Make explainability and monitoring release requirements

**Evidence.** No persisted SHAP artifacts were found. Production drift and outcome monitoring is not implemented in the snapshot.

**Action.** Add global and local SHAP analysis, model cards, cohort stability tests, explanation review, drift baselines, outcome dashboards, override tracking, and incident thresholds.

**Measures.** Share of models with approved card/SHAP pack; feature and prediction drift; calibration/error; override rate; incident detection and recovery time.

**Owner and gate.** Model Risk owner. High-impact use remains human-in-the-loop until sustained outcome evidence is available.

## Prioritized roadmap

| Horizon | Deliverable | Exit criterion |
|---|---|---|
| 0–30 days | cash and supplier action councils; canonical data contracts | owners, thresholds, reconciled baselines approved |
| 31–60 days | missing APIs, remote MLflow, secure container and CI | test/security/model gates pass in staging |
| 61–90 days | monitored human-in-the-loop pilots | business and guardrail metrics reported against baseline |
| 90+ days | selective automation and optimization | stable outcomes, rollback evidence, governance approval |
