# NexaChain Intelligence Platform Documentation

This documentation set consolidates the repository evidence available on August 3, 2026. It is written for GitBook publication and distinguishes implemented behavior from target-state contracts.

## Delivery map

| Module | Scope | Entry point |
|---|---|---|
| 5 | Data lineage and metric traceability bridge | [`module-5-lineage/README.md`](module-5-lineage/README.md) |
| 6 | API integration and developer guidance | [`module-6-api/api_integration_guide.md`](module-6-api/api_integration_guide.md) |
| 7 | AI platform GitBook | [`module-7-gitbook/SUMMARY.md`](module-7-gitbook/SUMMARY.md) |
| 8 | Final data science report | [`module-8-report/final_data_science_report.md`](module-8-report/final_data_science_report.md) |

## Evidence policy

- **Implemented** means a route, schema, model loader, and automated tests are present in `app/`.
- **Specified** means a request/response contract exists in `Reports/Continuity Api Endpoint.md`, but no route is registered.
- **Proposed** means this documentation supplies a versioned target contract that still requires product approval and implementation.
- Sample prediction values illustrate the response shape; they are not production model guarantees.

## Snapshot limitations

Four of ten target prediction endpoints are implemented. Docker and CI/CD files are not present in the repository snapshot. MLflow file-based tracking exists for demand forecasting, but no registered-model evidence is present. SHAP production artifacts were not found. These gaps are surfaced throughout the documentation rather than represented as completed capabilities.
