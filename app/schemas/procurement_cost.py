from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductCategory(str, Enum):
    precision = "Precision"
    industrial = "Industrial"
    electronics = "Electronics"
    raw_materials = "Raw Materials"


class MarketConditions(str, Enum):
    stable = "stable"
    volatile = "volatile"
    rising = "rising"
    falling = "falling"


class ProcurementCostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vendor_id: str = Field(min_length=1, max_length=100, pattern=r".*\S.*")
    product_category: ProductCategory
    quantity: int = Field(gt=0)
    lead_time: int = Field(ge=0, description="Lead time in days")
    market_conditions: MarketConditions


class CostRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min: float = Field(ge=0, allow_inf_nan=False)
    max: float = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_range(self) -> "CostRange":
        if self.max < self.min:
            raise ValueError("cost range maximum must be greater than or equal to minimum")
        return self


class ProcurementCostPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estimated_procurement_cost: float = Field(ge=0, allow_inf_nan=False)
    cost_range: CostRange
    suggested_procurement_window: str = Field(min_length=1)
