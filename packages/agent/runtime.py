"""Bounded Pi subprocess: stdin carries context; no shell commands or file tools."""

import asyncio
import json
from pathlib import Path

from packages.shared.config import Settings
from packages.shared.errors import ProviderUnavailableError

ROOT = Path(__file__).resolve().parents[2]


async def generate(
    system: str,
    prompt: str,
    provider: str,
    settings: Settings,
    max_tokens: int = 900,
) -> str:
    if provider not in ("ollama", "anthropic", "gemini"):
        raise ProviderUnavailableError(
            "This provider is not integrated.", "PROVIDER_NOT_CONFIGURED"
        )
    model = settings.selected_model(provider)
    if provider == "anthropic" and (not settings.ANTHROPIC_API_KEY or not model):
        raise ProviderUnavailableError(
            "Set ANTHROPIC_API_KEY and ANTHROPIC_MODEL to use cloud generation.",
            "PROVIDER_NOT_CONFIGURED",
        )
    if provider == "gemini" and (not settings.GEMINI_API_KEY or not model):
        raise ProviderUnavailableError(
            "Set GEMINI_API_KEY and GEMINI_MODEL to use cloud generation.",
            "PROVIDER_NOT_CONFIGURED",
        )
    api_key = (
        settings.GEMINI_API_KEY
        if provider == "gemini"
        else (settings.ANTHROPIC_API_KEY if provider == "anthropic" else "ollama")
    )
    payload = json.dumps(
        {
            "system": system,
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "baseUrl": settings.OLLAMA_BASE_URL.rstrip("/") + "/v1",
            "apiKey": api_key,
            "maxTokens": max_tokens,
        }
    ).encode()
    try:
        process = await asyncio.create_subprocess_exec(
            settings.NODE_BINARY,
            str(ROOT / "apps/agent/bridge.mjs"),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
    except OSError as exc:
        raise ProviderUnavailableError(
            "Pi runtime is unavailable. Install Node and agent dependencies.", "AGENT_UNAVAILABLE"
        ) from exc
    try:
        stdout, _ = await asyncio.wait_for(
            process.communicate(payload), timeout=settings.MODEL_TIMEOUT_SECONDS
        )
    except (TimeoutError, asyncio.CancelledError) as exc:
        if process.returncode is None:
            process.kill()
        await process.communicate()
        if isinstance(exc, asyncio.CancelledError):
            raise
        raise ProviderUnavailableError("Model timed out. Try a shorter request.", "MODEL_TIMEOUT")
    try:
        result = json.loads(stdout)
        if (
            process.returncode
            or not isinstance(result, dict)
            or not isinstance(result.get("text"), str)
            or not result["text"].strip()
        ):
            raise ValueError("Invalid agent output")
        return result["text"]
    except (ValueError, TypeError) as exc:
        raise ProviderUnavailableError(
            "Generation failed. Check the selected model and Pi installation.", "GENERATION_FAILED"
        ) from exc
