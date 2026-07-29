from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app.models.loader import get_cash_flow_model
from app.schemas.cash_flow import CashFlowPrediction, CashFlowRequest
from app.schemas.common import ErrorResponse, SuccessResponse

router = APIRouter(prefix="/predict", tags=["Cash Flow Forecast"])


@router.post(
    "/cash-flow",
    response_model=SuccessResponse[CashFlowPrediction],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "Model unavailable"},
    },
    summary="Forecast cash flow",
    description="Forecasts weekly cash flow and returns the model's financial-health signal.",
)
def predict_cash_flow(
    payload: CashFlowRequest,
    model: Any = Depends(get_cash_flow_model),
) -> SuccessResponse[CashFlowPrediction]:
    raw_prediction = model.predict([payload.model_dump()])
    prediction = CashFlowPrediction.model_validate(raw_prediction)
    return SuccessResponse[CashFlowPrediction](
        model="Cash Flow Forecast",
        prediction=prediction,
        timestamp=datetime.now(timezone.utc),
    )
