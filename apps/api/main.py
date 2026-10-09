import time
import uuid
from contextlib import asynccontextmanager
from typing import Callable

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routers.config import router as config_router
from apps.api.routers.health import router as health_router
from packages.shared.config import get_settings
from packages.shared.errors import AppError, app_error_exception_handler
from packages.shared.logging import configure_logging

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)
    logger.info("application_startup", provider=settings.LLM_PROVIDER.value)
    yield
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Lenny Growth Assistant API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and structured logging middleware
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
        )

        try:
            response: Response = await call_next(request)
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = request_id
            logger.info(
                "request_finished",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=latency_ms,
            )
            return response
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                latency_ms=latency_ms,
            )
            raise exc

    # Exception handler registration
    app.add_exception_handler(AppError, app_error_exception_handler)

    # Router registration
    app.include_router(health_router)
    app.include_router(config_router)

    return app


app = create_app()
