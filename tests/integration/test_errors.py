import uuid

from fastapi.testclient import TestClient
from pydantic import BaseModel

from apps.api.main import create_app
from packages.shared.errors import ProviderUnavailableError


class Payload(BaseModel):
    count: int


def error_client():
    app = create_app()

    @app.post("/test/validate")
    def validate(payload: Payload) -> Payload:
        return payload

    @app.get("/test/provider")
    def provider():
        raise ProviderUnavailableError()

    @app.get("/test/crash")
    def crash():
        raise RuntimeError("secret-database-password")

    return TestClient(app)


def test_validation_uses_envelope_without_echoing_input():
    response = error_client().post("/test/validate", json={"count": "secret-token"})
    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"
    assert "secret-token" not in response.text
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_not_found_uses_envelope():
    response = error_client().get("/missing")
    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"


def test_provider_failure_preserves_error_and_request_id():
    request_id = str(uuid.uuid4())
    response = error_client().get("/test/provider", headers={"X-Request-ID": request_id})
    assert response.status_code == 502
    assert response.json()["error_code"] == "PROVIDER_UNAVAILABLE"
    assert response.json()["request_id"] == request_id


def test_unexpected_failure_hides_internal_details():
    response = error_client().get("/test/crash")
    assert response.status_code == 500
    assert response.json()["error_code"] == "INTERNAL_ERROR"
    assert "secret-database-password" not in response.text
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_untrusted_request_id_is_replaced():
    response = error_client().get("/missing", headers={"X-Request-ID": "secret-token"})
    assert str(uuid.UUID(response.headers["X-Request-ID"])) == response.json()["request_id"]
