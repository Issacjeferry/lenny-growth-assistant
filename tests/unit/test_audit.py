from contextlib import contextmanager
from types import SimpleNamespace

from packages.retrieval import audit as module
from packages.retrieval.transcripts import parse_transcript


def test_audit_keeps_canonical_and_quarantines_alias_changed_and_missing(tmp_path, monkeypatch):
    source = tmp_path / "guest" / "transcript.md"
    source.parent.mkdir()
    source.write_text(
        "---\ntitle: Test\nguest: Test Guest\nyoutube_url: https://example.com/test\n---\nEvidence.",
        encoding="utf-8",
    )
    digest = parse_transcript(source).digest
    canonical = SimpleNamespace(
        source_path="guest/transcript.md", content_hash=digest, source_valid=False
    )
    alias = SimpleNamespace(
        source_path="episodes/guest/transcript.md", content_hash=digest, source_valid=True
    )
    missing = SimpleNamespace(
        source_path="missing/transcript.md", content_hash=digest, source_valid=True
    )
    commits = []

    @contextmanager
    def session():
        yield SimpleNamespace(
            scalars=lambda _: [alias, missing, canonical], commit=lambda: commits.append(True)
        )

    monkeypatch.setattr(module, "SessionLocal", session)
    result = module.audit(tmp_path)
    assert result["eligible"] == 1
    assert canonical.source_valid
    assert not alias.source_valid and not missing.source_valid
    assert len(result["quarantined"]) == 2
    assert commits == [True]
    canonical.content_hash = "changed"
    alias.content_hash = "changed"
    result = module.audit(tmp_path)
    assert result["eligible"] == 0
    assert not canonical.source_valid
