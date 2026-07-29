from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app.models.loader import get_working_capital_model
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.working_capital import WorkingCapitalPrediction, WorkingCapitalRequest

router = APIRouter(prefix="/predict", tags=["Working Capital Forecast"])


@router.post(
    "/working-capital",
    response_model=SuccessResponse[WorkingCapitalPrediction],
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    summary="Forecast working capital",
    description="Forecasts working capital and its liquidity trend for an inclusive date period.",
)
def predict_working_capital(
    payload: WorkingCapitalRequest,
    model: Any = Depends(get_working_capital_model),
) -> SuccessResponse[WorkingCapitalPrediction]:
    raw_prediction = model.predict([payload.model_dump(mode="json")])
    prediction = WorkingCapitalPrediction.model_validate(raw_prediction)
    return SuccessResponse[WorkingCapitalPrediction](
        model="Working Capital Forecast",
        prediction=prediction,
        timestamp=datetime.now(timezone.utc),
    )
