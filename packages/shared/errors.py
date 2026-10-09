from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from packages.shared.models import ErrorResponse


class AppError(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(message=message, error_code=error_code, status_code=404)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", error_code: str = "VALIDATION_ERROR"):
        super().__init__(message=message, error_code=error_code, status_code=400)


class ProviderUnavailableError(AppError):
    def __init__(
        self,
        message: str = "Provider unavailable",
        error_code: str = "PROVIDER_UNAVAILABLE",
    ):
        super().__init__(message=message, error_code=error_code, status_code=502)


class InternalError(AppError):
    def __init__(self, message: str = "Internal server error", error_code: str = "INTERNAL_ERROR"):
        super().__init__(message=message, error_code=error_code, status_code=500)


async def app_error_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppError):
        return error_response(request, exc.status_code, exc.error_code, exc.message)
    return error_response(request, 500, "INTERNAL_ERROR", "An unexpected error occurred")


def error_response(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
    payload = ErrorResponse(
        error_code=code,
        message=message,
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Do not echo submitted values: validation failures can contain credentials or prompts.
    return error_response(request, 422, "VALIDATION_ERROR", "Request validation failed")


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, HTTPException):
        return await app_error_exception_handler(request, exc)
    code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    response = error_response(request, exc.status_code, code, "Request could not be completed")
    if exc.headers:
        response.headers.update(exc.headers)
    return response
