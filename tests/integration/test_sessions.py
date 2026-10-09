from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.dependencies import get_db
from apps.api.main import create_app
from packages.agent import service
from packages.shared.db import Base
from packages.shared.db_models import Conversation, Message
from packages.shared.errors import ProviderUnavailableError
from tests.unit.test_agent import evidence


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    app = create_app()

    def database():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = database
    monkeypatch.setattr(service, "retrieve", AsyncMock(return_value=[evidence()]))
    monkeypatch.setattr(service, "generate", AsyncMock(return_value="Test advice [S1]"))
    with TestClient(app) as test_client:
        yield test_client, factory
    engine.dispose()


def test_sessions_persist_independent_context_and_metadata(client):
    api, factory = client
    first = api.post("/api/sessions", json={"user_metadata": {"team": "growth"}}).json()["id"]
    second = api.post("/api/sessions", json={}).json()["id"]
    response = api.post(f"/api/sessions/{first}/messages", json={"content": "Retention advice?"})
    assert response.status_code == 200
    assert response.json()["message"]["citations"][0]["title"] == "Synthetic test episode"
    assert len(api.get(f"/api/sessions/{first}").json()["messages"]) == 2
    assert api.get(f"/api/sessions/{second}").json()["messages"] == []
    with factory() as db:
        assert db.get(Conversation, first).user_metadata == {"team": "growth"}
        assert db.query(Message).count() == 2


def test_empty_retrieval_refuses_without_calling_model(client, monkeypatch):
    api, _ = client
    monkeypatch.setattr(service, "retrieve", AsyncMock(return_value=[]))
    generator = AsyncMock()
    monkeypatch.setattr(service, "generate", generator)
    session = api.post("/api/sessions", json={}).json()["id"]
    result = api.post(f"/api/sessions/{session}/messages", json={"content": "Unsupported?"}).json()
    assert result["message"]["status"] == "refused"
    assert result["message"]["citations"] == []
    generator.assert_not_called()


def test_failed_turn_rolls_back_and_can_be_retried(client, monkeypatch):
    api, _ = client
    session = api.post("/api/sessions", json={}).json()["id"]
    monkeypatch.setattr(service, "generate", AsyncMock(side_effect=ProviderUnavailableError()))
    result = api.post(f"/api/sessions/{session}/messages", json={"content": "Retention?"})
    assert result.status_code == 502
    assert api.get(f"/api/sessions/{session}").json()["messages"] == []


def test_html_artifact_is_sanitized_before_persistence(client, monkeypatch):
    api, _ = client
    monkeypatch.setattr(
        service, "generate", AsyncMock(return_value="<h1>Plan [S1]</h1><script>alert(1)</script>")
    )
    session = api.post("/api/sessions", json={}).json()["id"]
    result = api.post(
        f"/api/sessions/{session}/messages", json={"content": "Make a plan", "mode": "html"}
    ).json()
    assert "<script" not in result["artifact"]["content"]
    persisted = api.get(f"/api/sessions/{session}").json()["artifacts"]
    assert persisted[0]["content"] == result["artifact"]["content"]
