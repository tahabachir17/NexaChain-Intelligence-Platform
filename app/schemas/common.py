from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

PredictionT = TypeVar("PredictionT")


class SuccessResponse(BaseModel, Generic[PredictionT]):
    model_config = ConfigDict(extra="forbid")
    status: Literal["success"] = "success"
    model: str = Field(min_length=1)
    prediction: PredictionT
    timestamp: datetime


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["error"] = "error"
    message: str
    error_code: int
