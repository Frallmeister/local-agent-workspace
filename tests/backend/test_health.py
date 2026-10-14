"""Health API contract checks without external infrastructure."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from local_agent_workspace.api.routes.health import HealthResponse
from local_agent_workspace.main import app


def test_health_response() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ok"}


def test_openapi_health_contract() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    operation = schema["paths"]["/api/health"]["get"]
    response_schema = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]
    assert response_schema == {"$ref": "#/components/schemas/HealthResponse"}
    health_schema = schema["components"]["schemas"]["HealthResponse"]
    assert health_schema["type"] == "object"
    assert health_schema["required"] == ["status"]
    assert health_schema["properties"]["status"]["type"] == "string"
    assert health_schema["properties"]["status"]["const"] == "ok"


@pytest.mark.parametrize("payload", [{}, {"status": "error"}, {"status": 1}])
def test_health_model_rejects_invalid_status(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        HealthResponse.model_validate(payload)


def test_health_rejects_unsupported_method() -> None:
    with TestClient(app) as client:
        response = client.post("/api/health", json={"status": "ok"})
    assert response.status_code == 405
