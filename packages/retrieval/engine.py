"""Ollama embeddings and hybrid ranking with a semantic relevance gate."""

import math
import re

import httpx
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from packages.shared.config import Settings
from packages.shared.db_models import Chunk, Episode
from packages.shared.errors import ProviderUnavailableError


class Evidence(BaseModel):
    label: str = ""
    id: str
    title: str
    guest: str
    url: str
    excerpt: str
    timestamp_seconds: int | None
    distance: float


async def embed(texts: list[str], settings: Settings, query: bool = False) -> list[list[float]]:
    prefix = "search_query: " if query else "search_document: "
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/embed",
                json={
                    "model": settings.OLLAMA_EMBED_MODEL,
                    "input": [prefix + text for text in texts],
                    "truncate": True,
                },
            )
            response.raise_for_status()
            vectors = response.json()["embeddings"]
        if len(vectors) != len(texts) or any(
            len(v) != 768 or not all(math.isfinite(x) for x in v) for v in vectors
        ):
            raise ValueError("Invalid embedding dimensions")
        return vectors
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise ProviderUnavailableError(
            "Transcript search is unavailable. Check Ollama and nomic-embed-text.",
            "EMBEDDING_UNAVAILABLE",
        ) from exc


def fuse(vector_ids: list[str], keyword_ids: list[str]) -> list[str]:
    scores: dict[str, float] = {}
    for ranking in (vector_ids, keyword_ids):
        for rank, key in enumerate(dict.fromkeys(ranking), start=1):
            scores[key] = scores.get(key, 0) + 1 / (60 + rank)
    return sorted(scores, key=lambda key: (-scores[key], key))


def mentions_guest(query: str, guest: str) -> bool:
    """Prefer explicitly named guests, without matching first-name substrings."""
    words = re.findall(r"\w+", guest.casefold())
    if len(words) < 2:
        return False
    normalized = " " + " ".join(re.findall(r"\w+", query.casefold())) + " "
    return " " + " ".join(words) + " " in normalized


async def retrieve(query: str, db: Session, settings: Settings, limit: int = 5) -> list[Evidence]:
    if not db.scalar(select(func.count()).select_from(Chunk)):
        return []
    vector = (await embed([query], settings, query=True))[0]
    distance = Chunk.embedding.cosine_distance(vector)
    candidates = db.execute(
        select(Chunk, Episode, distance.label("distance"))
        .join(Episode, Chunk.episode_id == Episode.id)
        .where(Episode.source_valid.is_(True))
        .order_by(distance)
        .limit(30)
    ).all()
    eligible = {
        chunk.id: (chunk, episode, float(d))
        for chunk, episode, d in candidates
        if d <= settings.MAX_COSINE_DISTANCE
    }
    tsquery = func.websearch_to_tsquery("english", query)
    document = func.to_tsvector("english", Chunk.content)
    keyword_ids = list(
        db.scalars(
            select(Chunk.id)
            .where(document.op("@@")(tsquery))
            .order_by(func.ts_rank(document, tsquery).desc())
            .limit(30)
        )
    )
    order = fuse(list(eligible), [key for key in keyword_ids if key in eligible])
    # Stable preference keeps hybrid rank within each group and retains the relevance gate.
    order.sort(key=lambda key: not mentions_guest(query, eligible[key][1].guest))
    evidence = []
    seen_urls: dict[str, int] = {}
    seen_text = set()
    for key in order:
        chunk, episode, d = eligible[key]
        # Avoid filling the context with near-identical passages from one episode.
        count = seen_urls.get(episode.source_url, 0)
        if count >= 2 or chunk.content in seen_text:
            continue
        seen_text.add(chunk.content)
        seen_urls[episode.source_url] = count + 1
        url = episode.source_url
        if chunk.timestamp_seconds is not None and "youtube.com/watch?" in url:
            url += f"&t={chunk.timestamp_seconds}s"
        evidence.append(
            Evidence(
                id=key,
                title=episode.title,
                guest=episode.guest,
                url=url,
                excerpt=chunk.content,
                timestamp_seconds=chunk.timestamp_seconds,
                distance=d,
            )
        )
        if len(evidence) >= limit:
            break
    return evidence
