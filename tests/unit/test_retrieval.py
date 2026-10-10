from unittest.mock import AsyncMock

import httpx
import pytest

from packages.retrieval.engine import embed, fuse
from packages.retrieval.transcripts import parse_transcript
from packages.shared.config import Settings
from packages.shared.errors import ProviderUnavailableError


def transcript_file(tmp_path, body="Guest (00:01:30):\n" + "Retention matters. " * 500):
    path = tmp_path / "transcript.md"
    path.write_text(
        "---\ntitle: Synthetic test episode\nguest: Test Guest\n"
        "youtube_url: https://example.com/test\n---\n" + body,
        encoding="utf-8",
    )
    return path


def test_chunks_preserve_exact_source_offsets_and_timestamp(tmp_path):
    path = transcript_file(tmp_path)
    record = parse_transcript(path)
    raw = path.read_text(encoding="utf-8")
    assert len(record.passages) > 1
    for chunk in record.passages:
        assert raw[chunk.start : chunk.end] == chunk.content
        assert len(chunk.content) <= 2400
        assert chunk.timestamp == 90
    assert record.passages[-1].end == len(raw)
    assert record.passages[1].start < record.passages[0].end


def test_parser_rejects_missing_provenance(tmp_path):
    path = tmp_path / "transcript.md"
    path.write_text("---\ntitle: Untraceable\n---\ntext", encoding="utf-8")
    with pytest.raises(ValueError, match="source URL"):
        parse_transcript(path)


def test_rrf_promotes_agreement_without_counting_duplicates():
    assert fuse(["a", "b", "c"], ["b", "b", "c"]) == ["b", "c", "a"]


@pytest.mark.asyncio
async def test_embedding_failure_is_not_reported_as_no_evidence(monkeypatch):
    monkeypatch.setattr(
        httpx.AsyncClient, "post", AsyncMock(side_effect=httpx.ConnectError("down"))
    )
    with pytest.raises(ProviderUnavailableError) as error:
        await embed(["retention"], Settings(_env_file=None))
    assert error.value.error_code == "EMBEDDING_UNAVAILABLE"


@pytest.mark.asyncio
async def test_embedding_dimension_mismatch_is_rejected(monkeypatch):
    response = httpx.Response(
        200,
        json={"embeddings": [[1.0, 2.0]]},
        request=httpx.Request("POST", "http://localhost/api/embed"),
    )
    monkeypatch.setattr(httpx.AsyncClient, "post", AsyncMock(return_value=response))
    with pytest.raises(ProviderUnavailableError):
        await embed(["retention"], Settings(_env_file=None))


def test_parser_reads_minute_second_timestamps(tmp_path):
    record = parse_transcript(transcript_file(tmp_path, "Guest (12:34):\nUseful evidence."))
    assert record.passages[0].timestamp == 754


def test_parser_quarantines_conflicting_named_guest(tmp_path):
    path = transcript_file(tmp_path)
    path.write_text(
        path.read_text().replace("Synthetic test episode", "Product advice | Bob Baxley"),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Guest conflicts"):
        parse_transcript(path)
