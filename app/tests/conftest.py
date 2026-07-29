from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.loader import (
    get_cash_flow_model,
    get_procurement_cost_model,
    get_profitability_model,
    get_working_capital_model,
)


class FakeCashFlowModel:
    def predict(self, rows):
        weeks = rows[0]["forecast_weeks"]
        values = [1000.0 - (week * 25.0) for week in range(weeks)]
        return {
            "cash_flow_forecast": values,
            "weekly_trend": [
                {"week": week + 1, "predicted_cash_flow": value}
                for week, value in enumerate(values)
            ],
            "financial_health_indicator": "healthy",
        }


class FakeWorkingCapitalModel:
    def predict(self, rows):
        row = rows[0]
        forecast = (
            row["accounts_receivable_balance"]
            + row["inventory_value"]
            - row["accounts_payable_balance"]
        )
        return {
            "forecasted_working_capital": forecast,
            "liquidity_trend": "improving",
            "confidence_score": 0.91,
        }


class FakeProcurementCostModel:
    def predict(self, rows):
        estimate = rows[0]["quantity"] * 12.5
        return {
            "estimated_procurement_cost": estimate,
            "cost_range": {"min": estimate * 0.9, "max": estimate * 1.1},
            "suggested_procurement_window": "within 7 days",
        }


class FakeProfitabilityModel:
    def predict(self, rows):
        profit = rows[0]["quantity"] * 8.0
        return {
            "expected_profit": profit,
            "profit_margin": 24.5,
            "profitability_category": "high",
        }


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides.update(
        {
            get_cash_flow_model: lambda: FakeCashFlowModel(),
            get_working_capital_model: lambda: FakeWorkingCapitalModel(),
            get_procurement_cost_model: lambda: FakeProcurementCostModel(),
            get_profitability_model: lambda: FakeProfitabilityModel(),
        }
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
