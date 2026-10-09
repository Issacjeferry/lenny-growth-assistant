import asyncio
import math
import time

import httpx

from packages.shared.config import Settings
from packages.shared.errors import ProviderUnavailableError
from packages.shared.logging import get_logger

semaphore = asyncio.Semaphore(4)

async def embed_batch(texts: list[str], settings: Settings, query: bool = False) -> list[list[float]]:
    prefix = "search_query: " if query else "search_document: "
    start = time.monotonic()
    
    async with semaphore:
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/embed",
                    json={
                        "model": settings.OLLAMA_EMBED_MODEL,
                        "input": [prefix + text for text in texts],
                        "truncate": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                
                if "embeddings" in data:
                    vectors = data["embeddings"]
                elif "embedding" in data:
                    vectors = data["embedding"]
                else:
                    raise ValueError(f"Unknown response shape from /api/embed: {data.keys()}")
            
            if len(vectors) != len(texts) or any(
                len(v) != 768 or not all(math.isfinite(x) for x in v) for v in vectors
            ):
                raise ValueError("Invalid embedding dimensions")
            
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise ProviderUnavailableError(
                "Transcript search is unavailable. Check Ollama and nomic-embed-text.",
                "EMBEDDING_UNAVAILABLE",
            ) from exc
            
    elapsed_ms = int((time.monotonic() - start) * 1000)
    get_logger().info("embed_batch", batch_size=len(texts), elapsed_ms=elapsed_ms)
    return vectors
