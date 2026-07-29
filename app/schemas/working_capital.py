from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LiquidityTrend(str, Enum):
    improving = "improving"
    stable = "stable"
    declining = "declining"


class WorkingCapitalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period_start: date
    period_end: date
    accounts_receivable_balance: float = Field(ge=0, allow_inf_nan=False)
    accounts_payable_balance: float = Field(ge=0, allow_inf_nan=False)
    inventory_value: float = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_period(self) -> "WorkingCapitalRequest":
        if self.period_end < self.period_start:
            raise ValueError("period_end must be on or after period_start")
        return self


class WorkingCapitalPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    forecasted_working_capital: float = Field(allow_inf_nan=False)
    liquidity_trend: LiquidityTrend
    confidence_score: float = Field(ge=0, le=1, allow_inf_nan=False)
