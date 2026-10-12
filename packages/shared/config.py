from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderType(str, Enum):
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/lenny"
    LLM_PROVIDER: LLMProviderType = LLMProviderType.OLLAMA
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "lenny-local"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = ""
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = ""
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    MODEL_TIMEOUT_SECONDS: int = Field(default=900, ge=1, le=900)
    NODE_BINARY: str = "node"
    LOG_LEVEL: str = "INFO"
    MAX_COSINE_DISTANCE: float = Field(default=0.35, ge=0, le=2)

    def selected_model(self, provider: str | None = None) -> str:
        choice = provider or self.LLM_PROVIDER.value
        return {
            "ollama": self.OLLAMA_MODEL,
            "anthropic": self.ANTHROPIC_MODEL,
            "openai": self.OPENAI_MODEL,
            "gemini": self.GEMINI_MODEL,
        }[choice]


@lru_cache
def get_settings() -> Settings:
    return Settings()
