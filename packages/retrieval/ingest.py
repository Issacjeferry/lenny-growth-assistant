"""Idempotent, per-episode transactional ingestion. Run with make ingest."""

import argparse
import asyncio
from pathlib import Path

from sqlalchemy import delete, select

from packages.retrieval.engine import embed
from packages.retrieval.transcripts import parse_transcript
from packages.shared.config import get_settings
from packages.shared.db import SessionLocal
from packages.shared.db_models import Chunk, Episode
from packages.shared.logging import configure_logging, get_logger


async def ingest(root: Path, limit: int | None = None) -> dict[str, int]:
    settings = get_settings()
    paths = sorted(root.rglob("transcript.md"))
    if not paths:
        raise ValueError(f"No transcript.md files found in {root}")
    if limit is not None:
        paths = paths[:limit]
    counts = {"indexed": 0, "skipped": 0, "chunks": 0}
    version = f"chars2400-overlap300-v1:{settings.OLLAMA_EMBED_MODEL}"
    for path in paths:
        transcript = parse_transcript(path)
        source_path = path.relative_to(root).as_posix()
        with SessionLocal() as db:
            episode = db.scalar(select(Episode).where(Episode.source_path == source_path))
            if (
                episode
                and episode.content_hash == transcript.digest
                and episode.index_version == version
            ):
                counts["skipped"] += 1
                continue
            vectors = []
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
    parser.add_argument("--path", type=Path, default=Path("data/raw/lennys-podcast-transcripts"))
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    configure_logging()
    print(asyncio.run(ingest(args.path, args.limit)))


if __name__ == "__main__":
    main()
