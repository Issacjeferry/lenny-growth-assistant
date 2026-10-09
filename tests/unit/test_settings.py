from packages.shared.config import Settings, get_settings


def test_default_settings_load():
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.LLM_PROVIDER.value == "ollama"
    assert settings.OLLAMA_MODEL == "llama3.1:8b"
    assert settings.OLLAMA_EMBED_MODEL == "nomic-embed-text"
    assert settings.MAX_COSINE_DISTANCE == 0.35
    assert settings.LOG_LEVEL == "INFO"
    assert "postgresql" in settings.DATABASE_URL
