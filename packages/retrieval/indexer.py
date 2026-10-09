"""Batch ingestion with db-based skipping and concurrency. Run with python -m packages.retrieval.indexer"""

import argparse
import asyncio
import json
import time
from pathlib import Path

from sqlalchemy import delete, select

from packages.retrieval.embedder import embed_batch
from packages.retrieval.transcripts import parse_transcript
from packages.shared.config import get_settings
from packages.shared.db import SessionLocal
from packages.shared.db_models import Chunk, Episode
from packages.shared.logging import configure_logging, get_logger


async def process_episode(path: Path, root: Path, force: bool) -> dict:
    settings = get_settings()
    transcript = parse_transcript(path)
    source_path = path.relative_to(root).as_posix()
    slug = path.parent.name
    version = f"chars2400-overlap300-v1:{settings.OLLAMA_EMBED_MODEL}"
    
    start = time.monotonic()
    
    with SessionLocal() as db:
        episode = db.scalar(select(Episode).where(Episode.source_path == source_path))
        
        if episode and episode.content_hash == transcript.digest and not force:
            return {"slug": slug, "skipped": True, "chunks": 0}
        
        batch_size = 32
        passages = transcript.passages
        
        tasks = []
        for i in range(0, len(passages), batch_size):
            batch = passages[i:i+batch_size]
            tasks.append(embed_batch([p.content for p in batch], settings))
            
        batch_results = await asyncio.gather(*tasks)
        vectors = []
        for res in batch_results:
            vectors.extend(res)
            
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
        
        chunks = []
        for index, (passage, vector) in enumerate(zip(passages, vectors)):
            chunks.append(Chunk(
                episode_id=episode.id,
                chunk_index=index,
                content=passage.content,
                start_char=passage.start,
                end_char=passage.end,
                timestamp_seconds=passage.timestamp,
                embedding=vector,
            ))
        db.add_all(chunks)
        db.commit()
        
    elapsed_ms = int((time.monotonic() - start) * 1000)
    
    get_logger().info(
        "episode_ingested",
        episode_slug=slug,
        chunk_count=len(vectors),
        elapsed_ms=elapsed_ms
    )
    
    manifest_entry = {
        "slug": slug,
        "chunk_count": len(vectors),
        "content_hash": transcript.digest,
        "ingested_at": time.time()
    }
    return {"slug": slug, "skipped": False, "chunks": len(vectors), "manifest": manifest_entry}


async def ingest(root: Path, limit: int | None = None, force: bool = False, target_slug: str | None = None) -> dict[str, int]:
    paths = sorted(root.rglob("transcript.md"))
    if not paths:
        raise ValueError(f"No transcript.md files found in {root}")
        
    if target_slug:
        paths = [p for p in paths if p.parent.name == target_slug]
        
    if limit is not None:
        paths = paths[:limit]
        
    counts = {"indexed": 0, "skipped": 0, "chunks": 0}
    
    manifest_dir = Path("data/processed")
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "manifest.json"
    
    manifest_data = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, "r") as f:
                manifest_data = json.load(f)
        except Exception:
            pass
            
    for path in paths:
        result = await process_episode(path, root, force)
        
        if result["skipped"]:
            counts["skipped"] += 1
        else:
            counts["indexed"] += 1
            counts["chunks"] += result["chunks"]
            manifest_data[result["slug"]] = result["manifest"]
            
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f, indent=2)
                
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=Path("data/raw/episodes"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--slug", type=str)
    args = parser.parse_args()
    configure_logging()
    
    print(asyncio.run(ingest(args.path, args.limit, args.force, args.slug)))


if __name__ == "__main__":
    main()
