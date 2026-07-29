import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ModelUnavailableError(RuntimeError):
    """Raised when a configured prediction model cannot serve a request."""


def _error(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message, "error_code": status_code},
    )


def _validation_message(errors: list[dict[str, Any]]) -> str:
    first = errors[0]
    location = [str(part) for part in first.get("loc", ()) if part != "body"]
    field = ".".join(location) or "request body"
    if str(first.get("type", "")) == "missing":
        return f"{field} is required."
    return f"Invalid {field}: {first.get('msg', 'invalid value')}."


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        logger.warning("request_validation_failed", extra={"path": request.url.path, "errors": exc.errors()})
        return _error(_validation_message(exc.errors()), 400)

    @app.exception_handler(ValidationError)
    async def prediction_validation_handler(request: Request, exc: ValidationError):
        logger.exception("invalid_model_output", extra={"path": request.url.path})
        return _error("The model returned an invalid prediction.", 500)

    @app.exception_handler(ModelUnavailableError)
    async def model_unavailable_handler(request: Request, exc: ModelUnavailableError):
        logger.error("model_unavailable", extra={"path": request.url.path, "reason": str(exc)})
        return _error("The requested model is currently unavailable.", 503)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        message = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
        return _error(message, exc.status_code)

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_exception", extra={"path": request.url.path})
        return _error("An internal server error occurred.", 500)
