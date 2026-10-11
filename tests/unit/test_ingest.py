from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from packages.retrieval import ingest as module
from packages.shared.db import Base
from packages.shared.db_models import Chunk, Episode
from packages.shared.errors import ProviderUnavailableError


@pytest.mark.asyncio
async def test_ingestion_skip_refresh_and_failed_embedding_preserve_stored_passages(
    tmp_path, monkeypatch
):
    engine = create_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    monkeypatch.setattr(module, "SessionLocal", factory)
    embedding = AsyncMock(side_effect=lambda texts, settings: [[0.1] * 768 for _ in texts])
    monkeypatch.setattr(module, "embed", embedding)
    source = tmp_path / "guest" / "transcript.md"
    source.parent.mkdir()
    original = (
        "---\ntitle: Test\nguest: Test Guest\n"
        "youtube_url: https://example.com/episode\n---\nRetention is important."
    )
    source.write_text(original, encoding="utf-8")
    assert (await module.ingest(tmp_path))["indexed"] == 1
    assert (await module.ingest(tmp_path))["skipped"] == 1
    assert embedding.await_count == 1
    source.write_text(original + " A changed passage.", encoding="utf-8")
    embedding.side_effect = ProviderUnavailableError()
    with pytest.raises(ProviderUnavailableError):
        await module.ingest(tmp_path)
    with factory() as db:
        assert db.scalar(select(Chunk)).content == "Retention is important."
        assert db.scalar(select(Episode)).source_valid
    source.write_text("Invalid metadata", encoding="utf-8")
    assert (await module.ingest(tmp_path))["failed"] == 1
    with factory() as db:
        assert not db.scalar(select(Episode)).source_valid
        assert db.scalar(select(Chunk)).content == "Retention is important."
    source.write_text(original, encoding="utf-8")
    assert (await module.ingest(tmp_path))["skipped"] == 1
    with factory() as db:
        assert db.scalar(select(Episode)).source_valid
    engine.dispose()
