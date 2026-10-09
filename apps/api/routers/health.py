import httpx
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db, get_settings_dep
from packages.shared.config import Settings
from packages.shared.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def check_health(
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> HealthResponse:
    # 1. Check Database
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "down"

    # 2. Check Ollama
    ollama_status = "ok"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags")
            if res.status_code != 200:
                ollama_status = "down"
    except Exception:
        ollama_status = "down"

    # 3. Determine overall status and HTTP response status code
    if db_status == "down":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        overall_status = "unhealthy"
    elif ollama_status == "down":
        response.status_code = status.HTTP_200_OK
        overall_status = "degraded"
    else:
        response.status_code = status.HTTP_200_OK
        overall_status = "ok"

    return HealthResponse(
        status=overall_status,
        database=db_status,
        ollama=ollama_status,
        provider=settings.LLM_PROVIDER.value,
        model=settings.OLLAMA_MODEL,
    )
