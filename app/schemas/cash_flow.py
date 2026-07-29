from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FinancialHealthIndicator(str, Enum):
    healthy = "healthy"
    at_risk = "at-risk"
    critical = "critical"


class CashFlowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    forecast_weeks: int = Field(ge=1, le=52, examples=[13])
    current_cash_position: float = Field(ge=0, allow_inf_nan=False, examples=[1_000_000])
    outstanding_payables: float = Field(ge=0, allow_inf_nan=False, examples=[250_000])
    expected_receivables: float = Field(ge=0, allow_inf_nan=False, examples=[400_000])


class WeeklyTrendPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    week: int = Field(ge=1, le=52)
    predicted_cash_flow: float = Field(allow_inf_nan=False)


class CashFlowPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cash_flow_forecast: list[float] = Field(min_length=1, max_length=52)
    weekly_trend: list[WeeklyTrendPoint] = Field(min_length=1, max_length=52)
    financial_health_indicator: FinancialHealthIndicator
