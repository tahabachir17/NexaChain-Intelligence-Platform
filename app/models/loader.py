import logging
from threading import RLock
from typing import Any, Mapping

from fastapi import Request

from app.core.exceptions import ModelUnavailableError

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = frozenset(
    {"working-capital", "cash-flow", "procurement-cost", "profitability"}
)


class ModelManager:
    """Loads configured MLflow pyfunc models once and retains them in memory."""

    def __init__(self, model_uris: Mapping[str, str]):
        self._model_uris = dict(model_uris)
        self._models: dict[str, Any] = {}
        self._failures: dict[str, str] = {}
        self._lock = RLock()

    def load_all(self) -> None:
        for name, uri in self._model_uris.items():
            self._load(name, uri)
        for name in sorted(SUPPORTED_MODELS - self._model_uris.keys()):
            logger.warning("model_not_configured", extra={"model_name": name})

    def _load(self, name: str, uri: str) -> None:
        with self._lock:
            if name in self._models:
                return
            try:
                import mlflow.pyfunc

                self._models[name] = mlflow.pyfunc.load_model(uri)
                logger.info("model_loaded", extra={"model_name": name, "model_uri": uri})
            except Exception as exc:
                self._failures[name] = str(exc)
                logger.exception("model_load_failed", extra={"model_name": name, "model_uri": uri})

    def get(self, name: str) -> Any:
        try:
            return self._models[name]
        except KeyError as exc:
            reason = self._failures.get(name, "model URI is not configured")
            raise ModelUnavailableError(f"{name}: {reason}") from exc

    def clear(self) -> None:
        self._models.clear()
        self._failures.clear()


def get_cash_flow_model(request: Request) -> Any:
    return request.app.state.model_manager.get("cash-flow")


def get_working_capital_model(request: Request) -> Any:
    return request.app.state.model_manager.get("working-capital")


def get_procurement_cost_model(request: Request) -> Any:
    return request.app.state.model_manager.get("procurement-cost")


def get_profitability_model(request: Request) -> Any:
    return request.app.state.model_manager.get("profitability")
