from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_get_config():
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "ollama"
    assert data["model"] == "llama3.1:8b"
    assert data["embed_model"] == "nomic-embed-text"
    assert data["max_cosine_distance"] == 0.35
