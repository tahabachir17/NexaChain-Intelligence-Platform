from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app.models.loader import get_procurement_cost_model
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.procurement_cost import ProcurementCostPrediction, ProcurementCostRequest

router = APIRouter(prefix="/predict", tags=["Procurement Cost Prediction"])


@router.post(
    "/procurement-cost",
    response_model=SuccessResponse[ProcurementCostPrediction],
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    summary="Predict procurement cost",
    description="Estimates procurement cost, its expected range, and a procurement window.",
)
def predict_procurement_cost(
    payload: ProcurementCostRequest,
    model: Any = Depends(get_procurement_cost_model),
) -> SuccessResponse[ProcurementCostPrediction]:
    raw_prediction = model.predict([payload.model_dump(mode="json")])
    prediction = ProcurementCostPrediction.model_validate(raw_prediction)
    return SuccessResponse[ProcurementCostPrediction](
        model="Procurement Cost Prediction",
        prediction=prediction,
        timestamp=datetime.now(timezone.utc),
    )
