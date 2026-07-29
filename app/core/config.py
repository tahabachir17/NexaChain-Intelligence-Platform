import json
import os
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    api_v1_prefix: str
    log_level: str
    model_uris: Mapping[str, str]


def _model_uris_from_env() -> Mapping[str, str]:
    configured: dict[str, str] = {}
    raw = os.getenv("MODEL_URIS_JSON", "").strip()
    if raw:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in parsed.items()
        ):
            raise ValueError("MODEL_URIS_JSON must map model names to URI strings")
        configured.update(parsed)
    endpoint_env_vars = {
        "working-capital": "WORKING_CAPITAL_MODEL_URI",
        "cash-flow": "CASH_FLOW_MODEL_URI",
        "procurement-cost": "PROCUREMENT_COST_MODEL_URI",
        "profitability": "PROFITABILITY_MODEL_URI",
    }
    for model_name, env_var in endpoint_env_vars.items():
        uri = os.getenv(env_var, "").strip()
        if uri:
            configured[model_name] = uri
    return MappingProxyType(configured)


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "ML Model Inference API"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        api_v1_prefix="/api/v1",
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        model_uris=_model_uris_from_env(),
    )
