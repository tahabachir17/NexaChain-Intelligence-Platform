from fastapi import APIRouter

from app.api.v1.endpoints.cash_flow import router as cash_flow_router
from app.api.v1.endpoints.procurement_cost import router as procurement_cost_router
from app.api.v1.endpoints.profitability import router as profitability_router
from app.api.v1.endpoints.working_capital import router as working_capital_router

router = APIRouter()
router.include_router(working_capital_router)
router.include_router(cash_flow_router)
router.include_router(procurement_cost_router)
router.include_router(profitability_router)

# The source specification does not provide contracts for these model slots.
# TODO(model-01): define name, inputs, outputs, model URI, endpoint, and tests.
# TODO(model-02): define name, inputs, outputs, model URI, endpoint, and tests.
# TODO(model-03): define name, inputs, outputs, model URI, endpoint, and tests.
# TODO(model-04): define name, inputs, outputs, model URI, endpoint, and tests.
# Model 05 is working-capital and is implemented.
# Model 06 is cash-flow and is implemented.
# Model 07 is procurement-cost and is implemented.
# Model 08 is profitability and is implemented.
# TODO(model-09): define name, inputs, outputs, model URI, endpoint, and tests.
# TODO(model-10): define name, inputs, outputs, model URI, endpoint, and tests.
