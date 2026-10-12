"""Typed public API contracts for the evidence workspace."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from packages.retrieval.engine import Evidence


class CreateSession(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(default="New conversation", min_length=1, max_length=160)
    user_metadata: dict[str, str] = Field(default_factory=dict, max_length=10)


class SessionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    created_at: datetime


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    content: str = Field(min_length=1, max_length=6000)
    mode: Literal["qa", "ship30", "html", "markdown"] = "qa"
    provider: Literal["ollama", "anthropic", "gemini"] | None = None


class MessageView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    citations: list[Evidence]
    provider: str | None
    model: str | None
    status: str
    created_at: datetime


class ArtifactView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    message_id: str
    title: str
    type: str
    content: str
    created_at: datetime


class SessionDetail(SessionView):
    messages: list[MessageView]
    artifacts: list[ArtifactView]


class ChatResponse(BaseModel):
    message: MessageView
    artifact: ArtifactView | None = None
    latency_ms: float


class LibraryStatus(BaseModel):
    episodes: int
    chunks: int
    embedding_model: str
    quarantined_episodes: int = 0
