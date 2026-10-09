from typing import Optional

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    database: str
    ollama: str
    provider: str
    model: str


class ConfigResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str
    embed_model: str
    max_cosine_distance: float
    available_providers: list[str] = []
    agent_runtime: str = "Pi Coding Agent"


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error_code: str
    message: str
    request_id: Optional[str] = None
