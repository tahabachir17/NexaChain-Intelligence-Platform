from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SalesChannel(str, Enum):
    online = "online"
    retail = "retail"
    wholesale = "wholesale"
    direct = "direct"


class ProfitabilityCategory(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    negative = "negative"


class ProfitabilityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    vendor: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    customer: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    quantity: int = Field(gt=0)
    sales_channel: SalesChannel


class ProfitabilityPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_profit: float = Field(allow_inf_nan=False)
    profit_margin: float = Field(allow_inf_nan=False, description="Profit margin percentage")
    profitability_category: ProfitabilityCategory
