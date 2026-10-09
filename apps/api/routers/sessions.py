import time
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db, get_settings_dep
from packages.agent.service import answer
from packages.shared.config import Settings
from packages.shared.contracts import (
    ArtifactView,
    ChatRequest,
    ChatResponse,
    CreateSession,
    LibraryStatus,
    MessageView,
    SessionDetail,
    SessionView,
)
from packages.shared.db_models import Artifact, Chunk, Conversation, Episode, Message
from packages.shared.errors import AppError, NotFoundError

router = APIRouter(prefix="/api", tags=["workspace"])


def conversation(db: Session, session_id: UUID) -> Conversation:
    result = db.get(Conversation, str(session_id))
    if result is None:
        raise NotFoundError("Conversation not found", "SESSION_NOT_FOUND")
    return result


@router.post("/sessions", response_model=SessionView, status_code=201)
def create_session(payload: CreateSession, db: Session = Depends(get_db)):
    record = Conversation(title=payload.title, user_metadata=payload.user_metadata)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/sessions", response_model=list[SessionView])
def list_sessions(db: Session = Depends(get_db)):
    return list(
        db.scalars(select(Conversation).order_by(Conversation.created_at.desc()).limit(100))
    )


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(session_id: UUID, db: Session = Depends(get_db)):
    record = conversation(db, session_id)
    messages = db.scalars(
        select(Message)
        .where(Message.session_id == record.id)
        .order_by(Message.created_at, Message.id)
    )
    artifacts = db.scalars(
        select(Artifact)
        .where(Artifact.session_id == record.id)
        .order_by(Artifact.created_at, Artifact.id)
    )
    return SessionDetail(
        **SessionView.model_validate(record).model_dump(),
        messages=[MessageView.model_validate(m) for m in messages],
        artifacts=[ArtifactView.model_validate(a) for a in artifacts],
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
):
    started = time.perf_counter()
    record = conversation(db, session_id)
    # Serialise turns per conversation across workers without blocking the event loop.
    # PostgreSQL transaction-scoped locks release on commit, rollback or disconnect.
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        locked = db.scalar(
            text("SELECT pg_try_advisory_xact_lock(hashtext(:id))"), {"id": record.id}
        )
        if not locked:
            raise AppError("This conversation is generating a reply.", "SESSION_BUSY", 409)
    structlog.contextvars.bind_contextvars(session_id=record.id)
    history = list(
        reversed(
            list(
                db.scalars(
                    select(Message)
                    .where(Message.session_id == record.id)
                    .order_by(Message.created_at.desc(), Message.id.desc())
                    .limit(12)
                )
            )
        )
    )
    db.add(Message(session_id=record.id, role="user", content=payload.content))
    if record.title == "New conversation":
        record.title = payload.content[:100]
    try:
        message, artifact = await answer(payload, record.id, history, db, settings)
        db.commit()
        db.refresh(message)
        if artifact:
            db.refresh(artifact)
    except Exception:
        db.rollback()
        raise
    elapsed = round((time.perf_counter() - started) * 1000, 2)
    structlog.get_logger().info(
        "answer_completed",
        model=message.model,
        latency_ms=elapsed,
        answer_status=message.status,
        citations=len(message.citations),
    )
    return ChatResponse(
        message=MessageView.model_validate(message),
        artifact=ArtifactView.model_validate(artifact) if artifact else None,
        latency_ms=elapsed,
    )


@router.get("/library", response_model=LibraryStatus)
def library(db: Session = Depends(get_db), settings: Settings = Depends(get_settings_dep)):
    return LibraryStatus(
        episodes=db.scalar(select(func.count()).select_from(Episode)) or 0,
        chunks=db.scalar(select(func.count()).select_from(Chunk)) or 0,
        embedding_model=settings.OLLAMA_EMBED_MODEL,
    )


async def database_exception_handler(request, exc: Exception):
    from packages.shared.errors import error_response

    return error_response(
        request, 503, "DATABASE_UNAVAILABLE", "Database is unavailable. Retry shortly."
    )
