from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from fastapi.testclient import TestClient

from apps.api.dependencies import get_db
from apps.api.main import app

client = TestClient(app)


def test_health_all_ok():
    mock_session = MagicMock()
    mock_session.execute.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = httpx.Response(200, json={"models": []})
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["database"] == "ok"
            assert data["ollama"] == "ok"
            assert data["provider"] == "ollama"
            assert data["model"] == "llama3.1:8b"
    finally:
        app.dependency_overrides.clear()


def test_health_ollama_down():
    mock_session = MagicMock()
    mock_session.execute.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection refused")
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["database"] == "ok"
            assert data["ollama"] == "down"
    finally:
        app.dependency_overrides.clear()


def test_health_db_down():
    mock_session = MagicMock()
    mock_session.execute.side_effect = Exception("DB connection failed")

    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = httpx.Response(200, json={"models": []})
            response = client.get("/health")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "down"
    finally:
        app.dependency_overrides.clear()
