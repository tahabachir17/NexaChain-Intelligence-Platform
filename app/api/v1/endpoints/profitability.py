from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app.models.loader import get_profitability_model
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.profitability import ProfitabilityPrediction, ProfitabilityRequest

router = APIRouter(prefix="/predict", tags=["Profitability Prediction"])


@router.post(
    "/profitability",
    response_model=SuccessResponse[ProfitabilityPrediction],
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    summary="Predict profitability",
    description="Predicts profit, margin percentage, and profitability category for a sale.",
)
def predict_profitability(
    payload: ProfitabilityRequest,
    model: Any = Depends(get_profitability_model),
) -> SuccessResponse[ProfitabilityPrediction]:
    raw_prediction = model.predict([payload.model_dump(mode="json")])
    prediction = ProfitabilityPrediction.model_validate(raw_prediction)
    return SuccessResponse[ProfitabilityPrediction](
        model="Profitability Prediction",
        prediction=prediction,
        timestamp=datetime.now(timezone.utc),
    )
