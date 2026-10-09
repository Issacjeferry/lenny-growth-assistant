from fastapi import APIRouter, Depends

from apps.api.dependencies import get_settings_dep
from packages.shared.config import Settings
from packages.shared.models import ConfigResponse

router = APIRouter(tags=["config"])


@router.get("/config", response_model=ConfigResponse)
async def get_config(
    settings: Settings = Depends(get_settings_dep),
) -> ConfigResponse:
    return ConfigResponse(
        provider=settings.LLM_PROVIDER.value,
        model=settings.OLLAMA_MODEL,
        embed_model=settings.OLLAMA_EMBED_MODEL,
        max_cosine_distance=settings.MAX_COSINE_DISTANCE,
    )
