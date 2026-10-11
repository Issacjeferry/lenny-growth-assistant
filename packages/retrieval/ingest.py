"""Idempotent, per-episode transactional ingestion. Run with make ingest."""

import argparse
import asyncio
from pathlib import Path

from sqlalchemy import delete, select

from packages.retrieval.engine import embed
from packages.retrieval.transcripts import conflicting_sources, parse_transcript
from packages.shared.config import get_settings
from packages.shared.db import SessionLocal
from packages.shared.db_models import Chunk, Episode
from packages.shared.logging import configure_logging, get_logger


async def ingest(
    root: Path, limit: int | None = None, force: bool = False, target_slug: str | None = None
) -> dict[str, int]:
    settings = get_settings()
    paths = sorted(root.rglob("transcript.md"))
    conflicts = conflicting_sources(paths)
    if target_slug:
        paths = [path for path in paths if path.parent.name == target_slug]
    if not paths:
        raise ValueError(f"No transcript.md files found in {root}")
    if limit is not None:
        if limit < 1:
            raise ValueError("Limit must be positive")
        paths = paths[:limit]
    counts = {"indexed": 0, "skipped": 0, "failed": 0, "chunks": 0}
    version = f"chars2400-overlap300-v1:{settings.OLLAMA_EMBED_MODEL}"
    for path in paths:
        source_path = f"{path.parent.name}/transcript.md"
        try:
            if path in conflicts:
                raise ValueError("Identical transcript body has conflicting source URLs")
            transcript = parse_transcript(path)
        except ValueError:
            with SessionLocal() as db:
                episode = db.scalar(select(Episode).where(Episode.source_path == source_path))
                if episode:
                    episode.source_valid = False
                    db.commit()
            counts["failed"] += 1
            get_logger().error(
                "transcript_invalid", source_path=source_path, error_code="INVALID_TRANSCRIPT"
            )
            continue
        with SessionLocal() as db:
            episode = db.scalar(select(Episode).where(Episode.source_path == source_path))
            if (
                episode
                and episode.content_hash == transcript.digest
                and episode.index_version == version
                and not force
            ):
                episode.source_valid = True
                db.commit()
                counts["skipped"] += 1
                continue
            vectors = []
            # Bound CPU/memory pressure instead of queuing an entire episode at once.
            for i in range(0, len(transcript.passages), 8):
                vectors.extend(
                    await embed([p.content for p in transcript.passages[i : i + 8]], settings)
                )
            if episode is None:
                episode = Episode(source_path=source_path)
                db.add(episode)
            episode.title = transcript.title
            episode.guest = transcript.guest
            episode.source_url = transcript.url
            episode.content_hash = transcript.digest
            episode.index_version = version
            episode.source_valid = True
            db.flush()
            db.execute(delete(Chunk).where(Chunk.episode_id == episode.id))
            for index, (passage, vector) in enumerate(zip(transcript.passages, vectors)):
                db.add(
                    Chunk(
                        episode_id=episode.id,
                        chunk_index=index,
                        content=passage.content,
                        start_char=passage.start,
                        end_char=passage.end,
                        timestamp_seconds=passage.timestamp,
                        embedding=vector,
                    )
                )
            db.commit()
            counts["indexed"] += 1
            counts["chunks"] += len(vectors)
            get_logger().info("episode_indexed", source_path=source_path, chunks=len(vectors))
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=Path("data/raw"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--slug")
    args = parser.parse_args()
    configure_logging()
    result = asyncio.run(ingest(args.path, args.limit, args.force, args.slug))
    print(result)
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
