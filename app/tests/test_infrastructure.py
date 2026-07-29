import sys
from types import ModuleType

from app.models.loader import ModelManager


EXPECTED_PATHS = {
    "/api/v1/predict/working-capital",
    "/api/v1/predict/cash-flow",
    "/api/v1/predict/procurement-cost",
    "/api/v1/predict/profitability",
}


def test_openapi_exposes_every_specified_endpoint(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert EXPECTED_PATHS <= paths.keys()
    for path in EXPECTED_PATHS:
        operation = paths[path]["post"]
        assert operation["tags"]
        assert operation["summary"]
        assert "400" in operation["responses"]


def test_model_manager_loads_each_configured_model_once(monkeypatch):
    calls = []
    sentinel = object()
    fake_mlflow = ModuleType("mlflow")
    fake_pyfunc = ModuleType("mlflow.pyfunc")

    def fake_load_model(uri):
        calls.append(uri)
        return sentinel

    fake_pyfunc.load_model = fake_load_model
    fake_mlflow.pyfunc = fake_pyfunc
    monkeypatch.setitem(sys.modules, "mlflow", fake_mlflow)
    monkeypatch.setitem(sys.modules, "mlflow.pyfunc", fake_pyfunc)

    manager = ModelManager({"cash-flow": "runs:/abc/model"})
    manager.load_all()
    manager.load_all()

    assert calls == ["runs:/abc/model"]
    assert manager.get("cash-flow") is sentinel


def test_unknown_route_uses_standard_safe_error(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {
        "status": "error",
        "message": "Not Found",
        "error_code": 404,
    }
